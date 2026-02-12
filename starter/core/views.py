from django.shortcuts import render
from .models import Condominio
from datetime import date

def index(request):
    # 1. Buscar os dados no Banco
    lista_condominios = Condominio.objects.all()

    # 2. Preparar o pacote de dados (Contexto)
    contexto = {
        'condominios': lista_condominios,
        'titulo': 'Lista de Condomínios - Virada',
        'hoje': date.today(),
    }

    # 3. Entregar o HTML (Template) preenchido
    return render(request, 'core/index.html', contexto)