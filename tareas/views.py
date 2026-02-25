from rest_framework import viewsets, generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth.models import User
from .models import Tarea, PerfilPato
from .serializers import TareaSerializer, RegisterSerializer, PerfilPatoSerializer, RankingSerializer


# ── Registro ─────────────────────────────────────────────────────────────────
class RegisterView(generics.CreateAPIView):
    queryset           = User.objects.all()
    serializer_class   = RegisterSerializer
    permission_classes = [permissions.AllowAny]


# ── CRUD tareas ───────────────────────────────────────────────────────────────
class TareaViewSet(viewsets.ModelViewSet):
    serializer_class   = TareaSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Tarea.objects.filter(usuario=self.request.user).order_by('-creada')

    def perform_create(self, serializer):
        serializer.save(usuario=self.request.user)


# ── Perfil propio (GET / PATCH) ───────────────────────────────────────────────
class PerfilPatoView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def _get_perfil(self, user):
        perfil, _ = PerfilPato.objects.get_or_create(usuario=user)
        return perfil

    def get(self, request):
        serializer = PerfilPatoSerializer(self._get_perfil(request.user))
        return Response(serializer.data)

    def patch(self, request):
        perfil     = self._get_perfil(request.user)
        serializer = PerfilPatoSerializer(perfil, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ── Perfil público de cualquier usuario ──────────────────────────────────────
class PerfilPublicoView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, username):
        try:
            user      = User.objects.get(username=username)
            perfil, _ = PerfilPato.objects.get_or_create(usuario=user)
        except User.DoesNotExist:
            return Response(
                {"detail": "Usuario no encontrado."},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = PerfilPatoSerializer(perfil)
        return Response(serializer.data)


# ── Ranking global ────────────────────────────────────────────────────────────
class RankingView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        try:
            limit = min(int(request.query_params.get('limit', 10)), 100)
        except (ValueError, TypeError):
            limit = 10

        top        = PerfilPato.objects.select_related('usuario').order_by('-puntos')[:limit]
        serializer = RankingSerializer(top, many=True)
        return Response(serializer.data)