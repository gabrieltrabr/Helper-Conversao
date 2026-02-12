from django.shortcuts import render, get_object_or_404
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

def detalhe_condominio(request, pk):
    # 1. Busca o condomínio específico ou dá erro 404 (não encontrado)
    condominio = get_object_or_404(Condominio, pk=pk)
    
    # 2. O Django já faz a mágica: como usamos 'related_name' no Model,
    # condominio.blocos.all() já traz todos os blocos deste condomínio.
    
    contexto = {
        'condominio': condominio,
    }
    return render(request, 'core/detalhe_condominio.html', contexto)