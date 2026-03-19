from django.shortcuts import render, get_object_or_404, redirect
from .models import Condominio, Apartamento, ArquivoApartamento
from datetime import date
import zipfile
import os
import io
import openpyxl
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.db.models import Q

@login_required(login_url='/login/')
def index(request):
    if request.user.is_superuser:
        condominios = Condominio.objects.all()
    else:
        condominios = Condominio.objects.filter(
            Q(usuarios=request.user) | Q(blocos__usuarios=request.user)
        ).distinct()
        
    return render(request, 'core/index.html', {'condominios': condominios})

@login_required(login_url='/login/')
def detalhe_condominio(request, pk):
    condominio = get_object_or_404(Condominio, pk=pk)

    if request.user.is_superuser or request.user in condominio.usuarios.all():
        blocos_permitidos = condominio.blocos.all()
    else:
        blocos_permitidos = condominio.blocos.filter(usuarios=request.user)

    if request.method == 'POST':
        apartamentos = Apartamento.objects.filter(bloco__condominio=condominio)
        
        for apto in apartamentos:
            apto.naturgy = f'naturgy_{apto.id}' in request.POST
            apto.ap_2p6 = f'ap_2p6_{apto.id}' in request.POST
            apto.exaustao_forcada = f'exaustao_{apto.id}' in request.POST

        Apartamento.objects.bulk_update(apartamentos, ['naturgy', 'ap_2p6', 'exaustao_forcada'])
        
        return redirect('detalhe_condominio', pk=condominio.pk)
    contexto = {
        'condominio': condominio,
        'blocos_permitidos': blocos_permitidos,
    }
    return render(request, 'core/detalhe_condominio.html', contexto)

def ficha_apartamento(request, pk):
    apto = get_object_or_404(Apartamento, pk=pk)

    if request.method == 'POST':
        apto.morador = request.POST.get('morador', '')
        apto.tecnico = request.POST.get('tecnico', '')
        apto.equipamento = request.POST.get('equipamento', '')
        apto.observacoes = request.POST.get('observacoes', '')
        apto.save()

        if 'arquivo_os' in request.FILES:
            ArquivoApartamento.objects.create(
                apartamento=apto, 
                arquivo=request.FILES['arquivo_os'], 
                tipo='OS'
            )

        if 'arquivo_video' in request.FILES:
            ArquivoApartamento.objects.create(
                apartamento=apto, 
                arquivo=request.FILES['arquivo_video'], 
                tipo='VIDEO'
            )
        
        if 'arquivo_os_ex' in request.FILES:
            ArquivoApartamento.objects.create(
                apartamento=apto, 
                arquivo=request.FILES['arquivo_os_ex'], 
                tipo='OS_EX'
            )

        if 'arquivo_video_ex' in request.FILES:
            ArquivoApartamento.objects.create(
                apartamento=apto, 
                arquivo=request.FILES['arquivo_video_ex'], 
                tipo='VIDEO_EX'
            )

        if 'arquivos_extras' in request.FILES:
            for arquivo_extra in request.FILES.getlist('arquivos_extras'):
                ArquivoApartamento.objects.create(
                    apartamento=apto, 
                    arquivo=arquivo_extra, 
                    tipo='EXTRA'
                )

        return redirect('ficha_apartamento', pk=apto.pk)

    contexto = {
        'apto': apto,
        'arquivos': apto.arquivos.all() 
    }
    return render(request, 'core/ficha_apartamento.html', contexto)

def deletar_arquivo(request, pk):
    arquivo = get_object_or_404(ArquivoApartamento, pk=pk)
    
    apto_id = arquivo.apartamento.id
    
    if request.method == 'POST':
        if arquivo.arquivo:
            arquivo.arquivo.delete()
        
        arquivo.delete()
    return redirect('ficha_apartamento', pk=apto_id)

def baixar_arquivos_condominio(request, pk):
    condominio = get_object_or_404(Condominio, pk=pk)

    buffer = io.BytesIO()
    
    with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        
        arquivos = ArquivoApartamento.objects.filter(apartamento__bloco__condominio=condominio)
        
        for arq in arquivos:
            
            if arq.arquivo and hasattr(arq.arquivo, 'path') and os.path.exists(arq.arquivo.path):
                
                nome_bloco = arq.apartamento.bloco.nome
                nome_arquivo = os.path.basename(arq.arquivo.name)
                caminho_dentro_do_zip = f"{condominio.nome}/Bloco-{nome_bloco}/{nome_arquivo}"
 
                zip_file.write(arq.arquivo.path, caminho_dentro_do_zip)
   
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/zip')
    response['Content-Disposition'] = f'attachment; filename="Arquivos_{condominio.nome}.zip"'
    return response

def exportar_planilha_condominio(request, pk):
    condominio = get_object_or_404(Condominio, pk=pk)
    
    wb = openpyxl.Workbook()
    
    apartamentos = Apartamento.objects.filter(bloco__condominio=condominio).select_related('bloco').order_by('bloco__nome', 'numero')

    # ==========================================
    # ABA 1: Listagem de Serviços (Comercial)
    # ==========================================
    ws1 = wb.active 
    ws1.title = "Serviços e Moradores"
    
    # Cabeçalhos da Aba 1
    ws1.append(['Bloco', 'Apartamento', 'Morador', 'Técnico', 'Equipamento', 'Exaustão', 'Tem OS?', 'Tem Vídeo?', 'Observações'])
    
    # Preenchendo os dados da Aba 1
    for apto in apartamentos:
        status_os = "Sim" if apto.tem_os or apto.tem_os_ex else "Não"
        status_video = "Sim" if apto.tem_video or apto.tem_video_ex else "Não"
        
        ws1.append([
            apto.bloco.nome,
            apto.numero,
            apto.morador,
            apto.tecnico,
            apto.equipamento,
            "Sim" if apto.exaustao_forcada else "Não",
            status_os,
            status_video,
            apto.observacoes
        ])

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="Relatorio_{condominio.nome}.xlsx"'
    
    wb.save(response)
    
    return response