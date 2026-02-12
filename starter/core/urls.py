from django.urls import path
from . import views

urlpatterns = [
    # Quando o usuário acessar vazio (''), chama a view 'index'
    path('', views.index, name='index'),
    
    # Futuramente teremos algo como:
    # path('condominio/<int:id>/', views.detalhe_condominio, name='detalhe'),
]