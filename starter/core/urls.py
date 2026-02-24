from django.urls import path
from . import views
from django.conf import settings # Importar settings
from django.conf.urls.static import static # Importar static

urlpatterns = [
    # Quando o usuário acessar vazio (''), chama a view 'index'
    path('', views.index, name='index'),
    path('condominio/<int:pk>/', views.detalhe_condominio, name='detalhe_condominio'),
    path('apartamento/<int:pk>/', views.ficha_apartamento, name='ficha_apartamento'),
    path('arquivo/<int:pk>/deletar/', views.deletar_arquivo, name='deletar_arquivo'),
    path('condominio/<int:pk>/baixar-arquivos/', views.baixar_arquivos_condominio, name='baixar_arquivos'),
    path('condominio/<int:pk>/exportar-planilha/', views.exportar_planilha_condominio, name='exportar_planilha'),
]

# Adicione isto no final: permite ver os arquivos salvos enquanto estiver testando no PC
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)