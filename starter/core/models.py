import os
from django.db import models
from django.utils.text import slugify

class Condominio(models.Model):
    nome = models.CharField(max_length=100)
    endereco = models.CharField(max_length=255, blank=True)
    data_criacao = models.DateTimeField()
    data_inicio = models.DateField(null=True, blank=True, verbose_name="Início do Serviço")
    data_fim = models.DateField(null=True, blank=True, verbose_name="Fim do Serviço")

    qtd_andares_padrao = models.PositiveIntegerField(default=0, help_text="Padrão para os blocos deste condomínio")
    qtd_ap_por_andar_padrao = models.PositiveIntegerField(default=0, help_text="Padrão de aptos por andar")
    qtd_saloes_festas = models.PositiveIntegerField(default=0, verbose_name="Qtd. Salões de Festas", help_text="Cria automaticamente um bloco de Áreas Comuns")
    def __str__(self):
        return self.nome
    
    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)

        # Se for um condomínio novo e tiver salões de festas definidos
        if is_new and self.qtd_saloes_festas > 0:
            # 1. Cria um Bloco especial chamado "Áreas Comuns"
            bloco_comum = self.blocos.create(
                nome="Áreas Comuns",
                qtd_andares=0, # Zero para não gerar apartamentos normais
                qtd_ap_por_andar=0
            )
            
            # 2. Cria os "Apartamentos" que na verdade são os salões
            for i in range(1, self.qtd_saloes_festas + 1):
                # Se for só 1, chama de "Salão de Festas", se for mais, numera (ex: Salão de Festas 2)
                nome_salao = "Salão de Festas" if self.qtd_saloes_festas == 1 else f"Salão de Festas {i}"
                bloco_comum.apartamentos.create(numero=nome_salao)
    
    @property
    def total_apartamentos(self):
        return Apartamento.objects.filter(bloco__condominio=self).count()

    @property
    def total_aps_naturgy(self):
        return Apartamento.objects.filter(naturgy=True, bloco__condominio=self).count()
    
    @property
    def total_aps_2p6(self):
        return Apartamento.objects.filter(ap_2p6=True, bloco__condominio=self).count()
    
    @property
    def total_outros(self):
        return Apartamento.objects.filter(naturgy=False, bloco__condominio=self).count()

    @property
    def total_os(self):
        from .models import Apartamento
        # Filtra pela relação (arquivos) e pelo tipo. Usa distinct() para não contar o mesmo AP duas vezes
        return Apartamento.objects.filter(bloco__condominio=self, arquivos__tipo='OS').distinct().count()

    @property
    def total_videos(self):
        from .models import Apartamento
        return Apartamento.objects.filter(bloco__condominio=self, arquivos__tipo='VIDEO').distinct().count()

    @property
    def total_completos(self):
        from .models import Apartamento
        # Aqui fazemos um "AND" (E): Tem arquivo OS E tem arquivo VIDEO
        return Apartamento.objects.filter(
            bloco__condominio=self, arquivos__tipo='OS'
        ).filter(arquivos__tipo='VIDEO').distinct().count()
    
    @property
    def total_exaustao(self):
        from .models import Apartamento
        # Conta apartamentos distintos que têm OS ou Vídeo de exaustão
        return Apartamento.objects.filter(
            bloco__condominio=self, 
            arquivos__tipo__in=['OS_EX', 'VIDEO_EX']
        ).distinct().count()

class Bloco(models.Model):
    condominio = models.ForeignKey('Condominio', on_delete=models.CASCADE, related_name='blocos')
    nome = models.CharField(max_length=50)
    
    qtd_andares = models.PositiveIntegerField(null=True, blank=True, help_text="Quantos andares tem o prédio?")
    qtd_ap_por_andar = models.PositiveIntegerField(null=True, blank=True, help_text="Quantos apartamentos por andar?")
    inicio_numeracao = models.PositiveIntegerField(default=101, help_text="Qual é o primeiro apartamento? ex: 101")

    def __str__(self):
        return f"{self.condominio.nome} - {self.nome}"

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        andares_efetivos = self.qtd_andares if self.qtd_andares is not None else self.condominio.qtd_andares_padrao
        aps_por_andar_efetivos = self.qtd_ap_por_andar if self.qtd_ap_por_andar is not None else self.condominio.qtd_ap_por_andar_padrao
        super().save(*args, **kwargs)

        if is_new and andares_efetivos > 0:
            self.gerar_apartamentos(andares_efetivos, aps_por_andar_efetivos)

    def gerar_apartamentos(self, andares, aps_por_andar):
        """Agora recebe os valores como argumento"""
        objetos_apartamento = []
        
        for andar in range(1, andares + 1):
            for ap in range(1, aps_por_andar + 1):
                # Formatação: Ex: Andar 1, Ap 1 -> 101. Andar 12, Ap 4 -> 1204
                numero_ap = f"{andar}{ap:02d}" 
                
                # Prepara o objeto, mas não salva ainda (mais rápido)
                objetos_apartamento.append(
                    Apartamento(bloco=self, numero=numero_ap)
                )

        Apartamento.objects.bulk_create(objetos_apartamento, ignore_conflicts=True)

class Apartamento(models.Model):
    bloco = models.ForeignKey(Bloco, on_delete=models.CASCADE, related_name='apartamentos')
    numero = models.CharField(max_length=10)
    naturgy = models.BooleanField(default=False)
    ap_2p6 = models.BooleanField(default=False)
    
    morador = models.CharField(max_length=100, blank=True, verbose_name="Nome do Morador")
    tecnico = models.CharField(max_length=100, blank=True, verbose_name="Técnico Responsável")
    equipamento = models.CharField(max_length=200, blank=True, verbose_name="Equipamento(s)", help_text="Ex: Fogão 4 bocas, Aquecedor Lorenzetti")
    observacoes = models.TextField(blank=True, verbose_name="Observações / Impedimentos")
    
    @property
    def tem_os(self):
        # Retorna True se existir pelo menos 1 arquivo do tipo OS
        return self.arquivos.filter(tipo='OS').exists()

    @property
    def tem_video(self):
        # Retorna True se existir pelo menos 1 arquivo do tipo VIDEO
        return self.arquivos.filter(tipo='VIDEO').exists()

    exaustao_forcada = models.BooleanField(default=False)

    # 2. Adicione os atalhos lá no final da classe Apartamento:
    @property
    def tem_os_ex(self):
        return self.arquivos.filter(tipo='OS_EX').exists()

    @property
    def tem_video_ex(self):
        return self.arquivos.filter(tipo='VIDEO_EX').exists()

    # Vamos atualizar a inteligência do alerta de pendência para incluir a exaustão
    @property
    def pendente_parcial(self):
        pendencia_padrao = (self.tem_os and not self.tem_video) or (self.tem_video and not self.tem_os)
        tem_algum_ex = self.tem_os_ex or self.tem_video_ex
        pendencia_exaustao = tem_algum_ex and not (self.tem_os_ex and self.tem_video_ex)
        return pendencia_padrao or pendencia_exaustao

    class Meta:
        ordering = ['numero']

    def __str__(self):
        return f"{self.bloco} - Apto {self.numero}"
    
def caminho_arquivo_personalizado(instance, filename):
    # Pega a extensão original (.pdf, .mp4, .jpg)
    extensao = os.path.splitext(filename)[1].lower()
    
    # Pega os dados do relacionamento
    apto = instance.apartamento
    bloco = apto.bloco
    cond = bloco.condominio
    
    # slugify limpa espaços e caracteres estranhos. Ex: "Bloco A" vira "bloco-a"
    nome_bloco = slugify(bloco.nome).upper()
    
    # Monta o nome: BLOCO-APTO-TIPO-C{ID_CONDOMINIO}.ext
    # Ex: A-101-OS-C5.pdf  ou  BLOCO-B-204-VIDEO-C5.mp4
    novo_nome = f"{nome_bloco}-{apto.numero}-{instance.tipo}-C{cond.id}{extensao}"
    
    # Salva organizando em pastas separadas por condomínio
    return f"uploads/condominio_{cond.id}/{novo_nome}"

class ArquivoApartamento(models.Model):
    TIPO_CHOICES = [
        ('VIDEO', 'Vídeo'),
        ('OS', 'Ordem de Serviço'),
        ('EXTRA', 'Foto/Doc Extra'),
        ('OS_EX', 'OS Exaustão'),
    ]
    
    # A ligação mágica: O arquivo "sabe" a qual apartamento ele pertence
    apartamento = models.ForeignKey(Apartamento, on_delete=models.CASCADE, related_name='arquivos')
    
    arquivo = models.FileField(upload_to=caminho_arquivo_personalizado)
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES)
    data_envio = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.tipo} - {self.apartamento.numero}"