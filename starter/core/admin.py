
from django.contrib import admin
from .models import Condominio, Bloco, Apartamento

class BlocoInline(admin.TabularInline):
    model = Bloco
    extra = 1

@admin.register(Condominio)
class CondominioAdmin(admin.ModelAdmin):
    list_display = ('nome', 'endereco', 'data_criacao')
    inlines = [BlocoInline]

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

    def get_condominio(self, obj):
        return obj.bloco.condominio.nome
    get_condominio.short_description = 'Condomínio'

