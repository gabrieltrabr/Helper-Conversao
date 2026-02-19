from django.shortcuts import render, get_object_or_404, redirect
from .models import Condominio, Apartamento
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
    if request.method == 'POST':
        # Busca todos os apartamentos do condomínio
        apartamentos = Apartamento.objects.filter(bloco__condominio=condominio)
        
        # O HTML só manda no POST as caixas que estiverem marcadas
        for apto in apartamentos:
            apto.naturgy = f'naturgy_{apto.id}' in request.POST
            apto.ap_2p6 = f'ap_2p6_{apto.id}' in request.POST
            
        # bulk_update salva todos de uma só vez (eficiência máxima)
        Apartamento.objects.bulk_update(apartamentos, ['naturgy', 'ap_2p6'])
        
        return redirect('detalhe_condominio', pk=condominio.pk)
    contexto = {
        'condominio': condominio,
    }
    return render(request, 'core/detalhe_condominio.html', contexto)