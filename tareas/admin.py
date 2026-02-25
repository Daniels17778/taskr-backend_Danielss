from django.contrib import admin
from .models import Tarea, PerfilPato


@admin.register(Tarea)
class TareaAdmin(admin.ModelAdmin):
    list_display  = ('usuario', 'texto', 'hecha', 'creada')
    list_filter   = ('hecha',)
    search_fields = ('usuario__username', 'texto')
    ordering      = ('-creada',)


@admin.register(PerfilPato)
class PerfilPatoAdmin(admin.ModelAdmin):
    list_display  = ('usuario', 'nombre_pato', 'puntos', 'tareas_cumplidas', 'tareas_pendientes', 'accesorios_equipados')
    list_filter   = ()
    search_fields = ('usuario__username', 'nombre_pato')
    ordering      = ('-puntos',)
    readonly_fields = ('tareas_cumplidas', 'tareas_pendientes')

    @admin.display(description='Tareas cumplidas')
    def tareas_cumplidas(self, obj):
        return obj.tareas_cumplidas

    @admin.display(description='Tareas pendientes')
    def tareas_pendientes(self, obj):
        return obj.tareas_pendientes