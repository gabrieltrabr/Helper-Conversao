from django.shortcuts import render, get_object_or_404, redirect
from .models import Condominio, Apartamento, ArquivoApartamento
from datetime import date
import zipfile
import os
import io
import openpyxl
from django.http import HttpResponse

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
            apto.exaustao_forcada = f'exaustao_{apto.id}' in request.POST
        # bulk_update salva todos de uma só vez (eficiência máxima)
        Apartamento.objects.bulk_update(apartamentos, ['naturgy', 'ap_2p6', 'exaustao_forcada'])
        
        return redirect('detalhe_condominio', pk=condominio.pk)
    contexto = {
        'condominio': condominio,
    }
    return render(request, 'core/detalhe_condominio.html', contexto)

def ficha_apartamento(request, pk):
    apto = get_object_or_404(Apartamento, pk=pk)

    if request.method == 'POST':
        # 1. Salvar os campos de texto
        apto.morador = request.POST.get('morador', '')
        apto.tecnico = request.POST.get('tecnico', '')
        apto.equipamento = request.POST.get('equipamento', '')
        apto.observacoes = request.POST.get('observacoes', '')
        apto.save()

        # 2. Salvar Ordem de Serviço (Se enviada)
        if 'arquivo_os' in request.FILES:
            ArquivoApartamento.objects.create(
                apartamento=apto, 
                arquivo=request.FILES['arquivo_os'], 
                tipo='OS'
            )

        # 3. Salvar Vídeo (Se enviado)
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

        # Salvar Vídeo de Exaustão
        if 'arquivo_video_ex' in request.FILES:
            ArquivoApartamento.objects.create(
                apartamento=apto, 
                arquivo=request.FILES['arquivo_video_ex'], 
                tipo='VIDEO_EX'
            )

        # 4. Salvar Fotos Extras (Pode ser mais de uma, por isso usamos getlist)
        if 'arquivos_extras' in request.FILES:
            for arquivo_extra in request.FILES.getlist('arquivos_extras'):
                ArquivoApartamento.objects.create(
                    apartamento=apto, 
                    arquivo=arquivo_extra, 
                    tipo='EXTRA'
                )

        # Recarrega a página para mostrar os dados salvos
        return redirect('ficha_apartamento', pk=apto.pk)

    contexto = {
        'apto': apto,
        # Pegamos os arquivos já salvos para mostrar na tela
        'arquivos': apto.arquivos.all() 
    }
    return render(request, 'core/ficha_apartamento.html', contexto)

def deletar_arquivo(request, pk):
    # Encontra o arquivo ou dá erro 404
    arquivo = get_object_or_404(ArquivoApartamento, pk=pk)
    
    # Guardamos o ID do apartamento para poder voltar pra tela certa depois
    apto_id = arquivo.apartamento.id
    
    if request.method == 'POST':
        # 1. Apaga o arquivo físico do disco rígido (para não lotar o servidor)
        if arquivo.arquivo:
            arquivo.arquivo.delete()
        
        # 2. Apaga o registro do banco de dados
        arquivo.delete()
        
    # Redireciona de volta para a ficha do apartamento
    return redirect('ficha_apartamento', pk=apto_id)

def baixar_arquivos_condominio(request, pk):
    condominio = get_object_or_404(Condominio, pk=pk)
    
    # Cria um arquivo ZIP na memória (não gasta disco do servidor)
    buffer = io.BytesIO()
    
    with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        # Busca todos os arquivos deste condomínio
        arquivos = ArquivoApartamento.objects.filter(apartamento__bloco__condominio=condominio)
        
        for arq in arquivos:
            # Verifica se o arquivo físico realmente existe no disco
            if arq.arquivo and hasattr(arq.arquivo, 'path') and os.path.exists(arq.arquivo.path):
                # Monta a estrutura da pasta: "Condominio/Bloco-X/nome_do_arquivo.ext"
                nome_bloco = arq.apartamento.bloco.nome
                nome_arquivo = os.path.basename(arq.arquivo.name)
                caminho_dentro_do_zip = f"{condominio.nome}/Bloco-{nome_bloco}/{nome_arquivo}"
                
                # Escreve o arquivo dentro do ZIP na pasta correta
                zip_file.write(arq.arquivo.path, caminho_dentro_do_zip)
    
    # Prepara a resposta para o navegador baixar o arquivo
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/zip')
    response['Content-Disposition'] = f'attachment; filename="Arquivos_{condominio.nome}.zip"'
    return response

def exportar_planilha_condominio(request, pk):
    condominio = get_object_or_404(Condominio, pk=pk)
    
    # 1. Cria o arquivo Excel na memória
    wb = openpyxl.Workbook()
    
    # Para economizar consultas ao banco, buscamos todos os APs de uma vez só
    apartamentos = Apartamento.objects.filter(bloco__condominio=condominio).select_related('bloco').order_by('bloco__nome', 'numero')

    # ==========================================
    # ABA 1: Listagem de Serviços (Comercial)
    # ==========================================
    ws1 = wb.active # Pega a primeira aba criada por padrão
    ws1.title = "Serviços e Moradores"
    
    # Cabeçalhos da Aba 1
    ws1.append(['Bloco', 'Apartamento', 'Morador', 'Técnico', 'Equipamento', 'Exaustão', 'Tem OS?', 'Tem Vídeo?', 'Observações'])
    
    # Preenchendo os dados da Aba 1
    for apto in apartamentos:
        # Lógica para checar se tem OS/Vídeo (normal ou de exaustão)
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

    # 2. Prepara a resposta HTTP para o navegador baixar o arquivo
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="Relatorio_{condominio.nome}.xlsx"'
    
    # Salva o arquivo virtual direto na resposta
    wb.save(response)
    
    return response