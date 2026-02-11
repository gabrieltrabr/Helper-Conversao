from django.db import models


class Condominio(models.Model):
    nome = models.CharField(max_length=100)
    endereco = models.CharField(max_length=255, blank=True)
    data_criacao = models.DateTimeField()

    def __str__(self):
        return self.nome

class Bloco(models.Model):
    condominio = models.ForeignKey('Condominio', on_delete=models.CASCADE, related_name='blocos')
    nome = models.CharField(max_length=50)
    
    qtd_andares = models.PositiveIntegerField(default=0, help_text="Quantos andares tem o prédio?")
    qtd_ap_por_andar = models.PositiveIntegerField(default=0, help_text="Quantos apartamentos por andar?")
    inicio_numeracao = models.PositiveIntegerField(default=1, help_text="Qual é o primeiro apartamento? ex: 101")

    def __str__(self):
        return f"{self.condominio.nome} - {self.nome}"

    def save(self, *args, **kwargs):
        is_new = self.pk is None 
        super().save(*args, **kwargs)

        if is_new and self.qtd_andares > 0 and self.qtd_ap_por_andar > 0:
            self.gerar_apartamentos()

    def gerar_apartamentos(self):
        """Função auxiliar para criar os objetos Apartamento"""
        # Ex: 10 andares
        for andar in range(1, self.qtd_andares + 1):
            # Ex: 4 aptos por andar
            for ap in range(1, self.qtd_ap_por_andar + 1):
                # Lógica de numeração: Andar + Numero (com zero à esquerda se precisar)
                # Ex: Andar 1, Ap 1 -> "101"
                # Ex: Andar 10, Ap 2 -> "1002"
                
                # O :02d garante que o apto 1 vire '01' (101), apto 10 vire '10' (110)
                numero_ap = f"{andar}{ap:02d}" 
                
                # Criação segura (get_or_create evita duplicatas se rodar 2x)
                Apartamento.objects.get_or_create(
                    bloco=self,
                    numero=numero_ap
                )

class Apartamento(models.Model):
    bloco = models.ForeignKey(Bloco, on_delete=models.CASCADE, related_name='apartamentos')
    numero = models.CharField(max_length=10)
    naturgy = models.BooleanField(default=False)
    ap_2p6 = models.BooleanField(default=False)
    

    def __str__(self):
        return f"{self.bloco} - Apto {self.numero}"