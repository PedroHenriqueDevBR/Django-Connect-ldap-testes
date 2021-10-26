from django.contrib import admin
from django.urls import path
from django.contrib.auth.views import LoginView
from apps.core import views as core_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', LoginView.as_view(), name='login'),
    path('usuarios/', core_views.UsuariosView.as_view(), name='listagem_usuarios')
]
