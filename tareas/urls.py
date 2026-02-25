from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import RegisterView, TareaViewSet, PerfilPatoView, PerfilPublicoView, RankingView

router = DefaultRouter()
router.register(r'tareas', TareaViewSet, basename='tarea')

urlpatterns = [
    # Auth
    path('auth/register/', RegisterView.as_view(),        name='register'),
    path('auth/login/',    TokenObtainPairView.as_view(),  name='token_obtain_pair'),
    path('auth/refresh/',  TokenRefreshView.as_view(),     name='token_refresh'),

    # Tareas CRUD
    path('', include(router.urls)),

    # Perfil propio:  GET/PATCH  /api/perfil/
    path('perfil/',                         PerfilPatoView.as_view(),    name='perfil-pato'),

    # Perfil público: GET        /api/perfil-publico/<username>/
    path('perfil-publico/<str:username>/',  PerfilPublicoView.as_view(), name='perfil-publico'),

    # Ranking:        GET        /api/ranking/?limit=10
    path('ranking/',                        RankingView.as_view(),       name='ranking'),
]