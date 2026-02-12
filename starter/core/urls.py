from django.urls import path
from . import views

urlpatterns = [
    # Quando o usuário acessar vazio (''), chama a view 'index'
    path('', views.index, name='index'),
    path('condominio/<int:pk>/', views.detalhe_condominio, name='detalhe_condominio'),
    
]