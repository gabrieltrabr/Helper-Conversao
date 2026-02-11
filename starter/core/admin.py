
from django.contrib import admin
from .models import Condominio, Bloco, Apartamento

# Isso permite adicionar Blocos dentro da página do Condomínio
class BlocoInline(admin.TabularInline):
    model = Bloco
    extra = 1 # Quantos campos vazios aparecem por padrão

@admin.register(Condominio)
class CondominioAdmin(admin.ModelAdmin):
    list_display = ('nome', 'endereco', 'data_criacao')
    inlines = [BlocoInline]

# Isso permite adicionar Apartamentos dentro da página do Bloco
class ApartamentoInline(admin.TabularInline):
    model = Apartamento
    extra = 5

@admin.register(Bloco)
class BlocoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'condominio')
    list_filter = ('condominio',)
    inlines = [ApartamentoInline]

@admin.register(Apartamento)
class ApartamentoAdmin(admin.ModelAdmin):
    list_display = ('numero', 'get_condominio', 'bloco')
    list_filter = ('bloco__condominio', 'bloco')
    search_fields = ('numero',)

    # Função para exibir o condomínio na lista de apartamentos
    def get_condominio(self, obj):
        return obj.bloco.condominio.nome
    get_condominio.short_description = 'Condomínio'

