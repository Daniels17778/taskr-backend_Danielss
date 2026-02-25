from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Tarea, PerfilPato


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model  = User
        fields = ['username', 'password']

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class TareaSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Tarea
        fields = ['id', 'texto', 'hecha', 'creada']


class PerfilPatoSerializer(serializers.ModelSerializer):
    usuario           = serializers.CharField(source='usuario.username', read_only=True)
    avatar_url        = serializers.ReadOnlyField()
    tareas_cumplidas  = serializers.SerializerMethodField()
    tareas_pendientes = serializers.SerializerMethodField()

    class Meta:
        model  = PerfilPato
        fields = [
            'usuario',
            'nombre_pato',
            'puntos',
            'avatar_seed',   # editable: el usuario puede poner su handle de Twitter
            'avatar_url',    # solo lectura: URL construida automáticamente
            'accesorios_comprados',
            'accesorios_equipados',
            'tareas_cumplidas',
            'tareas_pendientes',
        ]
        read_only_fields = ['usuario', 'avatar_url', 'tareas_cumplidas', 'tareas_pendientes']

    def validate_avatar_seed(self, value):
        # Limpia espacios y fuerza minúsculas (Twitter handles)
        value = value.strip().lower()
        if not value:
            raise serializers.ValidationError("El seed no puede estar vacío.")
        # Verifica unicidad excluyendo el perfil actual
        qs = PerfilPato.objects.filter(avatar_seed=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("Ese handle de Twitter ya está en uso por otro usuario.")
        return value

    def get_tareas_cumplidas(self, obj):
        return obj.usuario.tareas.filter(hecha=True).count()

    def get_tareas_pendientes(self, obj):
        return obj.usuario.tareas.filter(hecha=False).count()


class RankingSerializer(serializers.ModelSerializer):
    usuario          = serializers.CharField(source='usuario.username', read_only=True)
    avatar_url       = serializers.ReadOnlyField()
    tareas_cumplidas = serializers.SerializerMethodField()

    class Meta:
        model  = PerfilPato
        fields = ['usuario', 'nombre_pato', 'puntos', 'avatar_url', 'tareas_cumplidas']

    def get_tareas_cumplidas(self, obj):
        return obj.usuario.tareas.filter(hecha=True).count()