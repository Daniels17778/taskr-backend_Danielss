import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from django.utils import timezone
from .models import Mensaje, PerfilPato


class ChatConsumer(AsyncWebsocketConsumer):
    """
    Maneja conexiones WebSocket para el chat.
    - Canal global:  ws://host/ws/chat/global/
    - Canal privado: ws://host/ws/chat/dm/<username_otro>/
    """

    async def connect(self):
        self.user = self.scope["user"]

        # Rechazar conexiones no autenticadas
        if not self.user or not self.user.is_authenticated:
            await self.close(code=4001)
            return

        self.sala = self.scope["url_route"]["kwargs"]["sala"]

        # Normalizar sala privada: siempre el mismo nombre sin importar quién inicia
        if self.sala.startswith("dm_"):
            partes = self.sala[3:].split("_")
            if len(partes) == 2:
                self.sala = "dm_" + "_".join(sorted(partes))

        self.group_name = f"chat_{self.sala}"

        # Unirse al grupo de Channels
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

        # Enviar historial reciente al conectar
        historial = await self.get_historial(self.sala)
        await self.send(text_data=json.dumps({
            "tipo":     "historial",
            "mensajes": historial,
        }))

    async def disconnect(self, close_code):
        if hasattr(self, "group_name"):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
        except json.JSONDecodeError:
            return

        tipo = data.get("tipo", "mensaje")

        if tipo == "mensaje":
            texto = data.get("texto", "").strip()
            if not texto or len(texto) > 1000:
                return

            # Guardar en BD
            msg = await self.guardar_mensaje(self.sala, texto)

            # Broadcast al grupo
            await self.channel_layer.group_send(
                self.group_name,
                {
                    "type":          "chat_message",
                    "id":            msg["id"],
                    "texto":         msg["texto"],
                    "usuario":       msg["usuario"],
                    "nombre_pato":   msg["nombre_pato"],
                    "accesorios":    msg["accesorios"],
                    "timestamp":     msg["timestamp"],
                }
            )

        elif tipo == "escribiendo":
            # Broadcast "X está escribiendo..."
            await self.channel_layer.group_send(
                self.group_name,
                {
                    "type":    "typing_event",
                    "usuario": self.user.username,
                    "activo":  data.get("activo", False),
                }
            )

    # ── Handlers de eventos del grupo ──────────────────────────────────────

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            "tipo":        "mensaje",
            "id":          event["id"],
            "texto":       event["texto"],
            "usuario":     event["usuario"],
            "nombre_pato": event["nombre_pato"],
            "accesorios":  event["accesorios"],
            "timestamp":   event["timestamp"],
        }))

    async def typing_event(self, event):
        # No enviar al propio usuario
        if event["usuario"] != self.user.username:
            await self.send(text_data=json.dumps({
                "tipo":    "escribiendo",
                "usuario": event["usuario"],
                "activo":  event["activo"],
            }))

    # ── DB helpers ──────────────────────────────────────────────────────────

    @database_sync_to_async
    def get_historial(self, sala, limite=60):
        mensajes = (
            Mensaje.objects
            .filter(sala=sala)
            .select_related("usuario", "usuario__perfil_pato")
            .order_by("-creado")[:limite]
        )
        resultado = []
        for m in reversed(mensajes):
            perfil = getattr(m.usuario, "perfil_pato", None)
            resultado.append({
                "id":          m.id,
                "texto":       m.texto,
                "usuario":     m.usuario.username,
                "nombre_pato": perfil.nombre_pato if perfil else "",
                "accesorios":  perfil.accesorios_equipados if perfil else [],
                "timestamp":   m.creado.isoformat(),
            })
        return resultado

    @database_sync_to_async
    def guardar_mensaje(self, sala, texto):
        msg    = Mensaje.objects.create(usuario=self.user, sala=sala, texto=texto)
        perfil = getattr(self.user, "perfil_pato", None)
        return {
            "id":          msg.id,
            "texto":       msg.texto,
            "usuario":     self.user.username,
            "nombre_pato": perfil.nombre_pato if perfil else "",
            "accesorios":  perfil.accesorios_equipados if perfil else [],
            "timestamp":   msg.creado.isoformat(),
        }