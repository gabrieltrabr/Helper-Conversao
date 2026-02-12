from django.db import models


class Condominio(models.Model):
    nome = models.CharField(max_length=100)
    endereco = models.CharField(max_length=255, blank=True)
    data_criacao = models.DateTimeField()
    data_inicio = models.DateField(null=True, blank=True, verbose_name="Início do Serviço")
    data_fim = models.DateField(null=True, blank=True, verbose_name="Fim do Serviço")

    qtd_andares_padrao = models.PositiveIntegerField(default=0, help_text="Padrão para os blocos deste condomínio")
    qtd_ap_por_andar_padrao = models.PositiveIntegerField(default=0, help_text="Padrão de aptos por andar")

    def __str__(self):
        return self.nome

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
    

    def __str__(self):
        return f"{self.bloco} - Apto {self.numero}"