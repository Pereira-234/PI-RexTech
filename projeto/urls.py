"""
URL configuration for projeto project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from rexapp import views 
from django.conf.urls.static import static
from django.conf import settings


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name= 'home'),
    path('login/', views.login_view, name='login'),
    path('sign-up/', views.sign_up_view, name='sign-up'),
    path('produto/<int:id>/', views.detalhar, name='detalhar_produto'),
    path('hardware/', views.hardware, name='hardware'),
    path('perfil/', views.perfil_view, name='perfil'),
    path('perfil/editar/', views.editar_perfil_view, name='editar_perfil'),
    path('logout/', views.logout_view, name='logout'), 
    path('produto/<int:produto_id>/', views.detalhe_produto, name='detalhe_produto'),
    path('produto/<int:produto_id>/avaliar/', views.avaliar_produto, name='avaliar_produto'),
    
    path('admin_page/', views.admin_dashboard, name='admin_dashboard'),
    path('admin_page/produtos/', views.admin_produtos_list, name='admin_produtos_list'),
    path('admin_page/produtos/add/', views.admin_produto_add, name='admin_produto_add'),
    path('admin_page/produtos/edit/<int:pk>/', views.admin_produto_edit, name='admin_produto_edit'),
    path('admin_page/produtos/delete/<int:pk>/', views.admin_produto_delete, name='admin_produto_delete'),

    path('admin_page/usuarios/', views.admin_usuarios_list, name='admin_usuarios_list'),
    path('admin_page/usuarios/add/', views.admin_usuario_add, name='admin_usuario_add'),
    path('admin_page/usuarios/edit/<int:pk>/', views.admin_usuario_edit, name='admin_usuario_edit'),
    path('admin_page/usuarios/delete/<int:pk>/', views.admin_usuario_delete, name='admin_usuario_delete'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
