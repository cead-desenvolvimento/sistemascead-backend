from datetime import date

import requests
from dal import autocomplete

from django.contrib import admin, messages
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import path, reverse
from django.utils import timezone as tz
from django.utils.safestring import mark_safe
from django.utils.translation import activate, gettext_lazy as _

from cead.messages import (
    ERRO_INSERCAO_ED_PESSOA_VAGA_CAMPO_CHECKBOX,
    ERRO_INSERCAO_ED_PESSOA_VAGA_CAMPO_COMBOBOX,
    ERRO_INSERCAO_ED_PESSOA_VAGA_CAMPO_DATEBOX,
    INFO_ENTRE_CONTATO_SUPORTE,
)
from .admin_forms import (
    EdEditalAdminForm,
    EdEditalUnidadeForm,
    EdEditalUnidadeFormSet,
    EdVagaCampoCheckboxForm,
    EdVagaCampoComboboxForm,
    EdVagaCampoDateboxForm,
    TrEspacoFisicoForm,
)
from .messages import ERRO_FERIADOS_INSERCAO, OK_FERIADOS_INSERCAO
from .models import *


class CmPessoaAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = CmPessoa.objects.all()
        if self.q:
            qs = qs.filter(nome__icontains=self.q)
        return qs


### ACADEMICO
class AcCursoAdmin(admin.ModelAdmin):
    list_display = (
        "nome",
        "coordenador",
        "email",
        "ativo",
        "descricao",
        "perfil_egresso",
        "telefone_completo",
    )
    search_fields = [
        "nome",
        "cm_pessoa_coordenador__nome",
        "cm_pessoa_coordenador__cpf",
    ]

    def coordenador(self, obj):
        if obj.cm_pessoa_coordenador:
            return f"{obj.cm_pessoa_coordenador.nome} {obj.cm_pessoa_coordenador.cpf}"
        return "-"

    def telefone_completo(self, obj):
        if obj.ddd and obj.telefone:
            telefone = obj.telefone.strip()
            if len(telefone) == 9:
                return f"({obj.ddd}) {telefone[:3]} {telefone[3:6]} {telefone[6:]}"
            elif len(telefone) == 8:
                return f"({obj.ddd}) {telefone[:4]} {telefone[4:]}"
            else:
                return f"({obj.ddd}) {telefone}"
        return "-"

    telefone_completo.short_description = "Telefone"

    class Media:
        css = {"all": ("autocomplete_light/select2.css",)}
        js = ("autocomplete_light/jquery.init.js", "autocomplete_light/select2.js")

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "cm_pessoa_coordenador":
            kwargs["widget"] = autocomplete.ModelSelect2(url="cm_pessoa_autocomplete")
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class AcCursoOfertaPoloInline(admin.TabularInline):
    model = AcCursoOfertaPolo
    fields = ("ac_polo", "vagas")
    verbose_name_plural = "Polos associados"
    extra = 0

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related("ac_polo")
            .order_by("ac_polo__nome")
        )


class AcCursoOfertaAdmin(admin.ModelAdmin):
    inlines = [AcCursoOfertaPoloInline]

    list_display = ("curso", "numero", "inicio_sisuab", "inicio", "fim", "vagas")
    search_fields = ["ac_curso__nome"]

    def curso(self, obj):
        return obj.ac_curso.nome if obj.ac_curso else "-"


class AcCursoOfertaPoloAdmin(admin.ModelAdmin):
    list_display = ("curso_nome", "oferta_numero", "polo_nome", "vagas")
    search_fields = [
        "ac_curso_oferta__ac_curso__nome",
        "ac_polo__nome",
    ]
    list_filter = ["ac_polo", "ac_curso_oferta__ac_curso"]
    list_select_related = ["ac_curso_oferta__ac_curso", "ac_polo"]

    def curso_nome(self, obj):
        if obj.ac_curso_oferta and obj.ac_curso_oferta.ac_curso:
            return obj.ac_curso_oferta.ac_curso.nome
        return "-"

    def oferta_numero(self, obj):
        if obj.ac_curso_oferta:
            return obj.ac_curso_oferta.numero
        return "-"

    def polo_nome(self, obj):
        if obj.ac_polo:
            return obj.ac_polo.nome
        return "-"

    curso_nome.short_description = "Curso"
    oferta_numero.short_description = "Número da Oferta"
    polo_nome.short_description = "Polo"


class AcCursoTipoAdmin(admin.ModelAdmin):
    list_display = ("nome",)


class AcDisciplinaAdmin(admin.ModelAdmin):
    list_display = ("nome", "curso", "periodo", "carga_horaria", "ativa")
    search_fields = ["ac_curso__nome", "nome"]

    def curso(self, obj):
        if obj.ac_curso:
            return obj.ac_curso
        return "-"


class AcMantenedorAdmin(admin.ModelAdmin):
    list_display = (
        "nome",
        "responsavel",
        "cnpj_formatado",
        "email",
        "tipo",
        "telefone_completo",
        "logradouro",
        "numero",
        "complemento",
        "bairro",
        "cep",
        "municipio",
    )
    search_fields = ["nome"]

    def municipio(self, obj):
        if obj.cm_municipio:
            return obj.cm_municipio.get_municipio_uf()
        return "-"

    def telefone_completo(self, obj):
        if obj.ddd and obj.telefone:
            telefone = obj.telefone.strip()
            if len(telefone) == 9:
                return f"({obj.ddd}) {telefone[:3]} {telefone[3:6]} {telefone[6:]}"
            elif len(telefone) == 8:
                return f"({obj.ddd}) {telefone[:4]} {telefone[4:]}"
            else:
                return f"({obj.ddd}) {telefone}"
        return "-"

    telefone_completo.short_description = "Telefone"

    def cnpj_formatado(self, obj):
        if obj.cnpj:
            return obj.cnpj_formatado()
        return "-"

    cnpj_formatado.short_description = "CNPJ"


class AcPoloHorarioFuncionamentoInline(admin.TabularInline):
    model = AcPoloHorarioFuncionamento
    verbose_name = "Horário de funcionamento"
    verbose_name_plural = "Horários de funcionamento"
    fields = ("dia_semana", "hora_inicio", "hora_fim")
    ordering = ("dia_semana", "hora_inicio")
    extra = 0
    can_delete = True

    # Evitar erros de relacao reversa:
    def has_add_permission(self, request, obj=None):
        return True

    def has_change_permission(self, request, obj=None):
        return True

    def has_delete_permission(self, request, obj=None):
        return True


class AcPoloAdmin(admin.ModelAdmin):
    list_display = (
        "nome",
        "mantenedor",
        "coordenador",
        "email",
        "ativo",
        "latitude",
        "longitude",
        "apresentacao_resumida",
        "telefone_completo",
        "logradouro",
        "numero",
        "complemento",
        "bairro",
        "cep",
        "municipio",
    )

    inlines = [AcPoloHorarioFuncionamentoInline]

    def apresentacao_resumida(self, obj):
        if obj.apresentacao:
            return (
                obj.apresentacao[:50] + "..."
                if len(obj.apresentacao) > 50
                else obj.apresentacao
            )
        return "-"

    apresentacao_resumida.short_description = "Apresentação"

    def mantenedor(self, obj):
        if obj.ac_mantenedor:
            return obj.ac_mantenedor.nome
        return "-"

    def coordenador(self, obj):
        if obj.cm_pessoa_coordenador:
            return obj.cm_pessoa_coordenador.nome
        return "-"

    def municipio(self, obj):
        if obj.cm_municipio:
            return obj.cm_municipio.get_municipio_uf()
        return "-"

    def telefone_completo(self, obj):
        if obj.ddd and obj.telefone:
            telefone = obj.telefone.strip()
            if len(telefone) == 9:
                return f"({obj.ddd}) {telefone[:3]} {telefone[3:6]} {telefone[6:]}"
            elif len(telefone) == 8:
                return f"({obj.ddd}) {telefone[:4]} {telefone[4:]}"
            else:
                return f"({obj.ddd}) {telefone}"
        return "-"

    telefone_completo.short_description = "Telefone"

    class Media:
        css = {"all": ("autocomplete_light/select2.css",)}
        js = ("autocomplete_light/jquery.init.js", "autocomplete_light/select2.js")

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "cm_pessoa_coordenador":
            kwargs["widget"] = autocomplete.ModelSelect2(url="cm_pessoa_autocomplete")
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


### COMUM
class CmFormacaoAdmin(admin.ModelAdmin):
    list_display = ("nome", "titulacao")
    search_fields = ["nome"]

    def titulacao(self, obj):
        if obj.cm_titulacao:
            return obj.cm_titulacao
        return "-"


class DjUriAdmin(admin.ModelAdmin):
    list_display = ("uri", "descricao")


class DjGrupoUriAdmin(admin.ModelAdmin):
    list_display = ("auth_group", "dj_uri")


class CmMunicipioAdmin(admin.ModelAdmin):
    list_display = ("municipio", "uf")
    search_fields = ["municipio", "uf"]

    def uf(self, obj):
        if obj.cm_uf:
            return obj.cm_uf.uf
        return "-"

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "cm_uf":
            kwargs["label"] = "Unidade da Federação"
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class CmPessoaBancoAdminInline(admin.TabularInline):
    model = CmPessoaBanco
    extra = 0
    verbose_name_plural = "Bancos"


class CmPessoaEnderecoAdminInline(admin.TabularInline):
    model = CmPessoaEndereco
    extra = 0
    verbose_name_plural = "Endereços"


class CmPessoaTelefoneAdminInline(admin.TabularInline):
    model = CmPessoaTelefone
    extra = 0
    verbose_name_plural = "Telefones"


class CmPessoaAdmin(admin.ModelAdmin):
    list_display = ("nome", "cpf", "email")
    search_fields = ["nome", "cpf"]

    inlines = [
        CmPessoaBancoAdminInline,
        CmPessoaEnderecoAdminInline,
        CmPessoaTelefoneAdminInline,
    ]


class CmPessoaBancoAdmin(admin.ModelAdmin):
    list_display = (
        "pessoa",
        "codigo_banco",
        "agencia",
        "conta",
        "digito_verificador_conta",
    )
    search_fields = ["cm_pessoa__nome"]

    def pessoa(self, obj):
        if obj.cm_pessoa:
            return obj.cm_pessoa
        return "-"


class CmPessoaEnderecoAdmin(admin.ModelAdmin):
    # readonly_fields = ('pessoa',)
    list_display = (
        "pessoa",
        "logradouro",
        "numero",
        "complemento",
        "bairro",
        "cep",
        "municipio",
        "referencia",
    )

    def pessoa(self, obj):
        if obj.cm_pessoa:
            return obj.cm_pessoa
        return "-"

    def municipio(self, obj):
        if obj.cm_municipio:
            return obj.cm_municipio.get_municipio_uf()
        return "-"


class CmPessoaTelefoneAdmin(admin.ModelAdmin):
    list_display = ("pessoa", "telefone")
    search_fields = ["cm_pessoa__nome"]

    def pessoa(self, obj):
        if obj.cm_pessoa:
            return obj.cm_pessoa
        return "-"

    def telefone(self, obj):
        if obj.cm_telefone:
            return obj.cm_telefone
        return "-"


class CmTelefoneAdmin(admin.ModelAdmin):
    list_display = ("ddd", "numero")
    search_fields = ["ddd", "numero"]


class CmTitulacaoAdmin(admin.ModelAdmin):
    list_display = ("nome",)
    search_fields = ["nome"]


class CmUfAdmin(admin.ModelAdmin):
    list_display = ("sigla", "uf")
    search_fields = ["sigla", "uf"]


### EDITAIS
class EdCampoAdmin(admin.ModelAdmin):
    list_display = ("descricao",)


class EdCotaAdmin(admin.ModelAdmin):
    list_display = ("cota",)


class EdVagaCotaAdmin(admin.ModelAdmin):
    list_display = ("ed_vaga", "ed_cota")


class EdPessoaVagaCotaAdmin(admin.ModelAdmin):
    list_display = ("get_cm_pessoa", "get_ed_vaga_cota")

    def get_cm_pessoa(self, obj):
        return obj.cm_pessoa

    def get_ed_vaga_cota(self, obj):
        return obj.ed_vaga_cota

    get_cm_pessoa.short_description = "Pessoa"
    get_ed_vaga_cota.short_description = "Cota na vaga"


class EdEditalAdminEditaisAbertos(admin.SimpleListFilter):
    title = "editais abertos"
    parameter_name = "data_fim_inscricao"

    def lookups(self, request, model_admin):
        return (("abertos", "Abertos"),)

    def queryset(self, request, queryset):
        if self.value() == "abertos":
            return queryset.filter(data_fim_inscricao__gte=tz.now())


class EdVagaAdminInline(admin.TabularInline):
    model = EdVaga
    extra = 0
    verbose_name_plural = "Vagas"


class EdEditalUnidadeInline(admin.TabularInline):
    model = EdEditalUnidade
    form = EdEditalUnidadeForm
    formset = EdEditalUnidadeFormSet
    max_num = 1
    extra = 1

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        if db_field.name == "ed_unidade":
            kwargs["queryset"] = db_field.remote_field.model.objects.all()
            kwargs["empty_label"] = "CEAD"
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class EdEditalAdmin(admin.ModelAdmin):
    list_display = (
        "edital",
        "descricao",
        "curso",
        "data_inicio_inscricao",
        "data_fim_inscricao",
        "data_inicio_validacao",
        "data_fim_validacao",
        "data_validade",
        "multiplas_inscricoes",
    )
    list_filter = (EdEditalAdminEditaisAbertos,)
    form = EdEditalAdminForm

    def get_exclude(self, request, obj=None):
        return ["data_cadastro"]

    def edital(self, obj):
        return obj.numero_ano_edital()

    def curso(self, obj):
        return obj.ac_curso if obj else "-"

    inlines = [EdEditalUnidadeInline, EdVagaAdminInline]

    # Cria um link na tela de edicao do edital para ir para a vaga
    def change_view(self, request, object_id, form_url="", extra_context=None):
        obj = self.get_object(request, object_id)
        extra_context = extra_context or {}
        if obj is not None and obj.edvaga_set.exists():
            first_vaga_id = obj.edvaga_set.first().id
            vaga_edit_url = reverse("admin:cead_edvaga_change", args=[first_vaga_id])
        else:
            return HttpResponseRedirect(reverse("admin:cead_edvaga_add"))

        extra_context["vaga_edit_url"] = vaga_edit_url
        self.change_form_template = "admin/ir_para_vaga.html"
        return super().change_view(
            request, object_id, form_url, extra_context=extra_context
        )

    def get_changeform_initial_data(self, request):
        initial = super().get_changeform_initial_data(request)

        # Recupera o maior número já cadastrado para o ano atual
        ano_atual = tz.now().year
        ultimo_numero = (
            self.model.objects.filter(ano=ano_atual)
            .order_by("-numero")
            .values_list("numero", flat=True)
            .first()
        )

        proximo_numero = (ultimo_numero or 0) + 1
        initial["numero"] = proximo_numero
        initial["ano"] = ano_atual

        return initial


class EdEditalPessoaAdmin(admin.ModelAdmin):
    list_display = ("ed_edital", "cm_pessoa")
    search_fields = ["cm_pessoa__nome"]


class EdPessoaFormacaoAdmin(admin.ModelAdmin):
    list_display = ("pessoa", "formacao", "inicio", "fim")
    search_fields = ["cm_pessoa__nome"]

    def pessoa(self, obj):
        if obj.cm_pessoa:
            return obj.cm_pessoa
        return "-"

    def formacao(self, obj):
        if obj.cm_formacao:
            return obj.cm_formacao
        return "-"


class EdPessoaVagaCampoCheckboxAdmin(admin.ModelAdmin):
    list_display = ("pessoa", "ed_vaga_campo_checkbox")
    search_fields = ["cm_pessoa__nome"]

    def pessoa(self, obj):
        if obj.cm_pessoa:
            return obj.cm_pessoa
        return "-"

    def edital(self, obj):
        if obj.ed_vaga_campo_checkbox:
            return obj.ed_vaga_campo_checkbox
        return "-"


class EdPessoaVagaCampoComboboxAdmin(admin.ModelAdmin):
    list_display = ("pessoa", "ed_vaga_campo_combobox")
    search_fields = ["cm_pessoa__nome"]

    def pessoa(self, obj):
        if obj.cm_pessoa:
            return obj.cm_pessoa
        return "-"

    def edital(self, obj):
        if obj.ed_vaga_campo_combobox:
            return obj.ed_vaga_campo_combobox
        return "-"


class EdPessoaVagaCampoDateboxAdmin(admin.ModelAdmin):
    list_display = ("pessoa", "ed_vaga_campo_datebox")
    search_fields = ["cm_pessoa__nome"]

    def pessoa(self, obj):
        if obj.cm_pessoa:
            return obj.cm_pessoa
        return "-"

    def edital(self, obj):
        if obj.ed_vaga_campo_datebox:
            return obj.ed_vaga_campo_datebox
        return "-"


class EdPessoaVagaCampoCheckboxUploadAdmin(admin.ModelAdmin):
    list_display = ("pessoa", "checkbox", "caminho_arquivo", "validado")
    search_fields = ["ed_pessoa_vaga_campo_checkbox__cm_pessoa__nome"]

    def pessoa(self, obj):
        if (
            obj.ed_pessoa_vaga_campo_checkbox
            and obj.ed_pessoa_vaga_campo_checkbox.cm_pessoa
        ):
            return obj.ed_pessoa_vaga_campo_checkbox.cm_pessoa
        return "-"

    def checkbox(self, obj):
        if obj.ed_pessoa_vaga_campo_checkbox:
            return obj.ed_pessoa_vaga_campo_checkbox
        return "-"


class EdPessoaVagaCampoComboboxUploadAdmin(admin.ModelAdmin):
    list_display = ("pessoa", "combobox", "caminho_arquivo", "validado")
    search_fields = ["ed_pessoa_vaga_campo_combobox__cm_pessoa__nome"]

    def pessoa(self, obj):
        if (
            obj.ed_pessoa_vaga_campo_combobox
            and obj.ed_pessoa_vaga_campo_combobox.cm_pessoa
        ):
            return obj.ed_pessoa_vaga_campo_combobox.cm_pessoa
        return "-"

    def combobox(self, obj):
        if obj.ed_pessoa_vaga_campo_combobox:
            return obj.ed_pessoa_vaga_campo_combobox
        return "-"


class EdPessoaVagaCampoDateboxUploadAdmin(admin.ModelAdmin):
    list_display = ("pessoa", "datebox", "caminho_arquivo", "validado")
    search_fields = ["ed_pessoa_vaga_campo_datebox__cm_pessoa__nome"]

    def pessoa(self, obj):
        if (
            obj.ed_pessoa_vaga_campo_datebox
            and obj.ed_pessoa_vaga_campo_datebox.cm_pessoa
        ):
            return obj.ed_pessoa_vaga_campo_datebox.cm_pessoa
        return "-"

    def datebox(self, obj):
        if obj.ed_pessoa_vaga_campo_datebox:
            return obj.ed_pessoa_vaga_campo_datebox
        return "-"


class EdPessoaVagaConfirmacaoAdmin(admin.ModelAdmin):
    list_display = ("pessoa", "edital", "vaga")
    search_fields = ["cm_pessoa__nome"]

    def pessoa(self, obj):
        if obj.cm_pessoa:
            return obj.cm_pessoa
        return "-"

    def edital(self, obj):
        if obj.ed_vaga and obj.ed_vaga.ed_edital:
            return obj.ed_vaga.ed_edital.numero_ano_edital()
        return "-"

    def vaga(self, obj):
        if obj.ed_vaga:
            return obj.ed_vaga
        return "-"


class EdPessoaVagaInscricaoAdmin(admin.ModelAdmin):
    list_display = (
        "pessoa",
        "edital",
        "vaga",
        "pontuacao",
        "data",
        "codigo_pessoavagainscricao",
    )
    search_fields = ["cm_pessoa__nome"]
    fields = ("cm_pessoa", "ed_vaga", "pontuacao", "data", "codigo_pessoavagainscricao")
    readonly_fields = (
        "cm_pessoa",
        "ed_vaga",
        "pontuacao",
        "data",
        "codigo_pessoavagainscricao",
    )

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_view_permission(self, request, obj=None):
        return True

    def pessoa(self, obj):
        if obj.cm_pessoa:
            return obj.cm_pessoa
        return "-"

    def edital(self, obj):
        if obj.ed_vaga and obj.ed_vaga.ed_edital:
            return obj.ed_vaga.ed_edital.numero_ano_edital()
        return "-"

    def vaga(self, obj):
        if obj.ed_vaga:
            return obj.ed_vaga
        return "-"


class EdPessoaVagaJustificativaAdmin(admin.ModelAdmin):
    list_display = ("pessoa", "edital", "vaga", "justificativa")
    search_fields = ["cm_pessoa__nome"]

    def pessoa(self, obj):
        if obj.cm_pessoa:
            return obj.cm_pessoa
        return "-"

    def edital(self, obj):
        if obj.ed_vaga and obj.ed_vaga.ed_edital:
            return obj.ed_vaga.ed_edital.numero_ano_edital()
        return "-"

    def vaga(self, obj):
        if obj.ed_vaga:
            return obj.ed_vaga
        return "-"


class EdPessoaVagaValidacaoAdmin(admin.ModelAdmin):
    list_display = (
        "pessoa",
        "validador",
        "edital",
        "vaga",
        "pontuacao",
        "data",
        "codigo",
    )
    search_fields = ["cm_pessoa__nome"]
    fields = (
        "cm_pessoa",
        "cm_pessoa_responsavel_validacao",
        "ed_vaga",
        "pontuacao",
        "data",
        "codigo",
    )
    readonly_fields = fields

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_view_permission(self, request, obj=None):
        return True

    def pessoa(self, obj):
        if obj.cm_pessoa:
            return obj.cm_pessoa
        return "-"

    def validador(self, obj):
        if obj.cm_pessoa_responsavel_validacao:
            return obj.cm_pessoa_responsavel_validacao
        return "-"

    def edital(self, obj):
        if obj.ed_vaga and obj.ed_vaga.ed_edital:
            return obj.ed_vaga.ed_edital.numero_ano_edital()
        return "-"

    def vaga(self, obj):
        if obj.ed_vaga:
            return obj.ed_vaga
        return "-"

    def codigo(self, obj):
        if obj.codigo:
            return obj.codigo
        return "-"


class EdUnidadeAdmin(admin.ModelAdmin):
    list_display = ("id", "abreviacao", "nome")
    search_fields = ("abreviacao", "nome")
    ordering = ("nome",)


class EdVagaCampoCheckboxAdminInline(admin.TabularInline):
    model = EdVagaCampoCheckbox
    form = EdVagaCampoCheckboxForm
    extra = 0
    verbose_name_plural = "Checkboxes"

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        if db_field.name == "ed_campo":
            kwargs["queryset"] = EdCampo.objects.order_by("descricao")
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    class Media:
        css = {
            "all": ("css/admin/select.css",),
        }


class EdVagaCampoComboboxAdminInline(admin.TabularInline):
    model = EdVagaCampoCombobox
    form = EdVagaCampoComboboxForm
    extra = 0
    verbose_name_plural = "Comboboxes"

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        if db_field.name == "ed_campo":
            kwargs["queryset"] = EdCampo.objects.order_by("descricao")
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    class Media:
        css = {
            "all": ("css/admin/select.css",),
        }


class EdVagaCampoDateboxAdminInline(admin.TabularInline):
    model = EdVagaCampoDatebox
    form = EdVagaCampoDateboxForm
    extra = 0
    verbose_name_plural = "Dateboxes"

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        if db_field.name == "ed_campo":
            kwargs["queryset"] = EdCampo.objects.order_by("descricao")
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)

        formset.form.base_fields["multiplicador_fracao_pontuacao"].initial = 360

        return formset

    class Media:
        css = {
            "all": ("css/admin/select.css",),
        }


class EdVagaAdmin(admin.ModelAdmin):
    list_display = ("vaga", "edital", "vagas", "polo")

    def polo(self, obj):
        return obj.ac_polo if obj.ac_polo else "-"

    def vaga(self, obj):
        return obj.descricao

    def vagas(self, obj):
        return obj.quantidade

    def edital(self, obj):
        return obj.ed_edital.numero_ano_edital() if obj.ed_edital else "-"

    edital.short_description = "Edital"

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ["ed_edital"]
        return []

    inlines = [
        EdVagaCampoCheckboxAdminInline,
        EdVagaCampoComboboxAdminInline,
        EdVagaCampoDateboxAdminInline,
    ]
    change_form_template = "admin/salvar_campos_para_todas_as_vagas.html"

    # O link personalizado precisa receber o objeto, entao 'obj' vai para o template
    def change_view(self, request, object_id, form_url="", extra_context=None):
        extra_context = extra_context or {}
        extra_context["obj"] = self.get_object(request, object_id)
        return super().change_view(
            request, object_id, form_url, extra_context=extra_context
        )

    def response_change(self, request, obj):
        if "_salvar_para_todas_vagas" in request.POST:
            # Preciso pegar tudo que ta na tela para salvar para as outras vagas
            # Entao coloco tudo nos dicionarios e depois itero nas outras vagas do edital para salvar
            checkboxes_da_tela = {}
            for checkbox in obj.edvagacampocheckbox_set.all():
                checkbox_data = {
                    "campo": checkbox.ed_campo,
                    "pontuacao": checkbox.pontuacao,
                    "obrigatorio": checkbox.obrigatorio,
                    "assinado": checkbox.assinado,
                }
                checkboxes_da_tela[checkbox.id] = checkbox_data

            comboboxes_da_tela = {}
            for combobox in obj.edvagacampocombobox_set.all():
                combobox_data = {
                    "campo": combobox.ed_campo,
                    "descricao": combobox.descricao,
                    "ordem": combobox.ordem,
                    "pontuacao": combobox.pontuacao,
                    "obrigatorio": combobox.obrigatorio,
                    "assinado": combobox.assinado,
                }
                comboboxes_da_tela[combobox.id] = combobox_data

            dateboxes_da_tela = {}
            for datebox in obj.edvagacampodatebox_set.all():
                datebox_data = {
                    "campo": datebox.ed_campo,
                    "fracao_pontuacao": datebox.fracao_pontuacao,
                    "multiplicador_fracao_pontuacao": datebox.multiplicador_fracao_pontuacao,
                    "pontuacao_maxima": datebox.pontuacao_maxima,
                    "obrigatorio": datebox.obrigatorio,
                    "assinado": datebox.assinado,
                }
                dateboxes_da_tela[datebox.id] = datebox_data

            outras_vagas_do_edital = EdVaga.objects.filter(
                ed_edital=obj.ed_edital
            ).exclude(id=obj.id)

            ## ISSO AQUI NAO PODE SER FEITO SE ALGUEM JA MARCOU O CAMPO, DEVE SER TRATADO!
            # No minimo tem que ajustar o modelo para os delete cascade,
            # mas as mudancas que o usuario pode fazer sao imprevisiveis

            # Apaga os campos das outras vagas
            # Muito custoso cobrir tudo para tentar dar update em campo de outra vaga que:
            # 1) pode ter sido apagado
            # 2) pode ter sido editado
            # 3) pode ter campo novo que essa vaga nao tem
            for outra_vaga_do_edital in outras_vagas_do_edital:
                EdVagaCampoCheckbox.objects.filter(
                    ed_vaga=outra_vaga_do_edital
                ).delete()
                EdVagaCampoCombobox.objects.filter(
                    ed_vaga=outra_vaga_do_edital
                ).delete()
                EdVagaCampoDatebox.objects.filter(ed_vaga=outra_vaga_do_edital).delete()

                for chave, valor in checkboxes_da_tela.items():
                    try:
                        EdVagaCampoCheckbox.objects.create(
                            ed_vaga=outra_vaga_do_edital,
                            ed_campo=valor["campo"],
                            pontuacao=valor["pontuacao"],
                            obrigatorio=valor["obrigatorio"],
                            assinado=valor["assinado"],
                        )
                    except Exception as e:
                        messages.error(
                            request,
                            f"{ERRO_INSERCAO_ED_PESSOA_VAGA_CAMPO_CHECKBOX}: {e}",
                        )
                        messages.info(request, INFO_ENTRE_CONTATO_SUPORTE)

                for chave, valor in comboboxes_da_tela.items():
                    try:
                        EdVagaCampoCombobox.objects.create(
                            ed_vaga=outra_vaga_do_edital,
                            ed_campo=valor["campo"],
                            descricao=valor["descricao"],
                            ordem=valor["ordem"],
                            pontuacao=valor["pontuacao"],
                            obrigatorio=valor["obrigatorio"],
                            assinado=valor["assinado"],
                        )
                    except Exception as e:
                        messages.error(
                            request,
                            f"{ERRO_INSERCAO_ED_PESSOA_VAGA_CAMPO_COMBOBOX}: {e}",
                        )
                        messages.info(request, INFO_ENTRE_CONTATO_SUPORTE)

                for chave, valor in dateboxes_da_tela.items():
                    try:
                        EdVagaCampoDatebox.objects.create(
                            ed_vaga=outra_vaga_do_edital,
                            ed_campo=valor["campo"],
                            fracao_pontuacao=valor["fracao_pontuacao"],
                            multiplicador_fracao_pontuacao=valor[
                                "multiplicador_fracao_pontuacao"
                            ],
                            pontuacao_maxima=valor["pontuacao_maxima"],
                            obrigatorio=valor["obrigatorio"],
                            assinado=valor["assinado"],
                        )
                    except Exception as e:
                        messages.error(
                            request,
                            f"{ERRO_INSERCAO_ED_PESSOA_VAGA_CAMPO_DATEBOX}: {e}",
                        )
                        messages.info(request, INFO_ENTRE_CONTATO_SUPORTE)

        return super().response_change(request, obj)


class EdVagaCampoCheckboxAdmin(admin.ModelAdmin):
    list_display = ("vaga", "campo", "pontuacao", "obrigatorio")
    search_fields = ["ed_campo__descricao"]

    class Media:
        css = {
            "all": ("css/admin/select.css",),
        }

    def vaga(self, obj):
        if obj.ed_vaga:
            return obj.ed_vaga
        return "-"

    def campo(self, obj):
        if obj.ed_campo:
            return obj.ed_campo
        return "-"


class EdVagaCampoComboboxAdmin(admin.ModelAdmin):
    list_display = ("vaga", "campo", "descricao", "ordem", "pontuacao", "obrigatorio")
    search_fields = ["ed_campo__descricao"]

    class Media:
        css = {
            "all": ("css/admin/select.css",),
        }

    def vaga(self, obj):
        if obj.ed_vaga:
            return obj.ed_vaga
        return "-"

    def campo(self, obj):
        if obj.ed_campo:
            return obj.ed_campo
        return "-"


class EdVagaCampoDateboxAdmin(admin.ModelAdmin):
    list_display = (
        "vaga",
        "campo",
        "fracao_pontuacao",
        "multiplicador_fracao_pontuacao",
        "pontuacao_maxima",
        "obrigatorio",
    )
    search_fields = ["ed_campo__descricao"]

    class Media:
        css = {
            "all": ("css/admin/select.css",),
        }

    def vaga(self, obj):
        if obj.ed_vaga:
            return obj.ed_vaga
        return "-"

    def campo(self, obj):
        if obj.ed_campo:
            return obj.ed_campo
        return "-"


### FINANCEIRO
class FiDataFrequenciaAdmin(admin.ModelAdmin):
    list_display = ("periodo",)

    def periodo(self, obj):
        if obj.id:
            link = reverse(
                "admin:%s_%s_change" % (obj._meta.app_label, obj._meta.model_name),
                args=[obj.id],
            )
            return mark_safe('<a href="{}">{}</a>'.format(link, obj.__str__()))
        return "-"

    activate("pt-br")
    periodo.short_description = "Período"


class FiFrequenciaAdminCurrentMonthFilter(admin.SimpleListFilter):
    title = "mês corrente"
    parameter_name = "current_month"

    def lookups(self, request, model_admin):
        return (("current", "Mês corrente"),)

    def queryset(self, request, queryset):
        if self.value() == "current":
            today = tz.now()
            return queryset.filter(data__year=today.year, data__month=today.month)


class FiFrequenciaAdmin(admin.ModelAdmin):
    list_display = ("bolsista", "coordenador", "periodo", "data")
    list_filter = (FiFrequenciaAdminCurrentMonthFilter,)

    def bolsista(self, obj):
        if obj.cm_pessoa:
            return obj.cm_pessoa.nome
        return "-"

    def coordenador(self, obj):
        if obj.cm_pessoa_coordenador:
            return obj.cm_pessoa_coordenador.nome
        return "-"

    def periodo(self, obj):
        if obj.fi_datafrequencia:
            data_inicio = obj.fi_datafrequencia.data_inicio
            return f"{data_inicio.strftime('%B')} de {data_inicio.year}"
        return "-"


class FiFuncaoBolsistaAdmin(admin.ModelAdmin):
    list_display = ("funcao",)


class FiPessoaFichaAdminDataFimVInculacaoIsNull(admin.SimpleListFilter):
    title = _("fichas sem data fim de vinculação")
    parameter_name = "null_data_fim_vinculacao"

    def lookups(self, request, model_admin):
        return (("null", _("Fichas sem data fim de vinculação")),)

    def queryset(self, request, queryset):
        if self.value() == "null":
            return queryset.filter(data_fim_vinculacao__isnull=True)


class FiPessoaFichaAdmin(admin.ModelAdmin):
    list_display = (
        "bolsista",
        "edital",
        "oferta",
        "funcao",
        "data_inicio_vinculacao",
        "data_fim_vinculacao",
        "data_nascimento",
        "sexo",
        "profissao",
        "tipo_documento",
        "numero_documento",
        "orgao_expedidor",
        "data_emissao",
        "estado_civil",
        "nome_conjuge",
        "nome_pai",
        "nome_mae",
        "area_ultimo_curso_superior",
        "ultimo_curso_titulacao",
        "instituicao_titulacao",
    )
    list_filter = (FiPessoaFichaAdminDataFimVInculacaoIsNull,)
    search_fields = ("cm_pessoa__nome",)

    def get_readonly_fields(self, request, obj=None):
        return [f.name for f in self.model._meta.fields]

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return True

    # Busca por edital
    def get_search_results(self, request, queryset, search_term):
        queryset, use_distinct = super().get_search_results(
            request, queryset, search_term
        )

        if "/" in search_term:
            numero, ano = search_term.split("/")
            queryset |= self.model.objects.filter(
                ed_edital__numero=numero, ed_edital__ano=ano
            )
        return queryset, use_distinct

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name in ["cm_pessoa", "ed_edital"]:
            # Evita carregar o queryset inteiro e usa apenas o valor existente
            return None
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def bolsista(self, obj):
        if obj.cm_pessoa_id:
            return obj.cm_pessoa.nome
        return "-"

    def edital(self, obj):
        if obj.ed_edital:
            return obj.ed_edital.__str__()
        return "-"

    def oferta(self, obj):
        if obj.ed_edital:
            return obj.ac_curso_oferta.numero
        return "-"

    def funcao(self, obj):
        if obj.fi_funcao_bolsista:
            return obj.fi_funcao_bolsista.funcao
        return "-"


class FiFrequenciaDisciplinaAdmin(admin.ModelAdmin):
    list_display = ("frequencia", "pessoa", "disciplina")

    def frequencia(self, obj):
        if obj.fi_frequencia:
            return obj.fi_frequencia.fi_datafrequencia
        return "-"

    def pessoa(self, obj):
        if obj.fi_frequencia:
            return obj.fi_frequencia.cm_pessoa
        return "-"

    def disciplina(self, obj):
        if obj.ac_disciplina:
            return obj.ac_disciplina
        return "-"


### TRANSMISSÃO
class TrTermoAdmin(admin.ModelAdmin):
    list_display = ("termo",)
    search_fields = ("termo",)


class TrEspacoFisicoAdmin(admin.ModelAdmin):
    form = TrEspacoFisicoForm
    list_display = (
        "espaco_fisico",
        "dias_pre_transmissao",
        "dias_pos_transmissao",
        "ativo",
    )
    search_fields = ("espaco_fisico",)
    list_filter = ("ativo",)


class TrDisponibilidadeEquipeAdmin(admin.ModelAdmin):
    list_display = ("dia_semana", "inicio", "fim")
    list_filter = ("dia_semana",)
    ordering = ("dia_semana", "inicio")


class TrIndisponibilidadeEquipeAdmin(admin.ModelAdmin):
    list_display = ("data",)
    search_fields = ("data",)
    change_list_template = "admin/tr_indisponibilidade_equipe/change_list.html"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "importar-feriados/",
                self.admin_site.admin_view(self.importar_feriados),
                name="importar-feriados",
            ),
        ]
        return custom_urls + urls

    def importar_feriados(self, request):
        ano_atual = date.today().year
        try:
            resposta = requests.get(
                f"https://brasilapi.com.br/api/feriados/v1/{ano_atual}"
            )
            feriados = resposta.json()
        except Exception as e:
            self.message_user(
                request, f"{str(e)} - {ERRO_FERIADOS_INSERCAO}", messages.ERROR
            )
            return redirect("..")

        if request.method == "POST":
            inseridos = 0
            for feriado in feriados:
                data_feriado = feriado["date"]
                obj, created = TrIndisponibilidadeEquipe.objects.get_or_create(
                    data=data_feriado
                )
                if created:
                    inseridos += 1

            self.message_user(
                request, f"{OK_FERIADOS_INSERCAO}: {inseridos}", messages.SUCCESS
            )
            return redirect("..")

        # Se for GET, mostra a tela de confirmação com os feriados
        context = dict(
            self.admin_site.each_context(request),
            title="Importar feriados nacionais",
            opts=self.model._meta,
            feriados=feriados,
        )
        return render(
            request,
            "admin/tr_indisponibilidade_equipe/confirmar_importacao.html",
            context,
        )


class TrTransmissaoHorarioInline(admin.TabularInline):
    model = TrTransmissaoHorario
    extra = 0
    verbose_name = "Horário"
    verbose_name_plural = "Horários"
    fields = ("inicio", "fim")
    can_delete = False


class TrTransmissaoAdmin(admin.ModelAdmin):
    list_display = ("tr_termo", "tr_espaco_fisico", "cm_pessoa")
    readonly_fields = ("assinatura_digital",)
    search_fields = ("observacao",)
    inlines = [TrTransmissaoHorarioInline]

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "cm_pessoa":
            kwargs["widget"] = autocomplete.ModelSelect2(url="cm_pessoa_autocomplete")
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class TrTransmissaoEmailAdmin(admin.ModelAdmin):
    list_display = ("email", "tipo_email_envio")
    search_fields = ("email",)
    list_filter = ("tipo_email_envio",)


class TrTransmissaoRecusadaAdmin(admin.ModelAdmin):
    list_display = ("tr_transmissao", "observacao")
    search_fields = ("observacao", "tr_transmissao__id")
    list_filter = ("tr_transmissao",)


class TrLimitesAdmin(admin.ModelAdmin):
    list_display = (
        "maximo_por_mes",
        "maximo_por_semana",
        "maximo_dias_na_semana",
        "limite_por_pessoa",
        "dias_de_antecedencia",
        "dias_de_agenda_aberta",
        "evento_passando_de_semana",
    )
    readonly_fields = ("id",)
    fieldsets = (
        (
            "Limites globais das transmissões",
            {
                "fields": (
                    "maximo_por_mes",
                    "maximo_por_semana",
                    "maximo_dias_na_semana",
                    "limite_por_pessoa",
                    "dias_de_antecedencia",
                    "dias_de_agenda_aberta",
                    "evento_passando_de_semana",
                ),
                "description": (
                    "<b>Observação:</b> A precedência é mensal. "
                    "Se atingir o máximo por mês, não poderá agendar mais, "
                    "mesmo que não tenha atingido o limite semanal.<br>"
                    "Exemplo: se <i>máximo por mês</i> = 4 e <i>máximo por semana</i> = 3, "
                    "o usuário só poderá agendar 4 vezes no mês."
                ),
            },
        ),
    )

    def has_add_permission(self, request):
        # Impede criação de novas linhas pelo admin (singleton)
        count = TrLimites.objects.count()
        if count >= 1:
            return False
        return True

    def has_delete_permission(self, request, obj=None):
        # Impede remoção pelo admin (singleton)
        return False

    def save_model(self, request, obj, form, change):
        obj.id = 1
        super().save_model(request, obj, form, change)


admin.site.register(AcCurso, AcCursoAdmin)
admin.site.register(AcCursoOferta, AcCursoOfertaAdmin)
admin.site.register(AcCursoOfertaPolo, AcCursoOfertaPoloAdmin)
admin.site.register(AcCursoTipo, AcCursoTipoAdmin)
admin.site.register(AcDisciplina, AcDisciplinaAdmin)
admin.site.register(AcMantenedor, AcMantenedorAdmin)
admin.site.register(AcPolo, AcPoloAdmin)

admin.site.register(CmFormacao, CmFormacaoAdmin)
admin.site.register(DjUri, DjUriAdmin)
admin.site.register(DjGrupoUri, DjGrupoUriAdmin)
admin.site.register(CmMunicipio, CmMunicipioAdmin)
admin.site.register(CmPessoa, CmPessoaAdmin)
# admin.site.register(CmPessoaBanco, CmPessoaBancoAdmin)
# admin.site.register(CmPessoaEndereco, CmPessoaEnderecoAdmin)
# admin.site.register(CmPessoaTelefone, CmPessoaTelefoneAdmin)
admin.site.register(CmTitulacao, CmTitulacaoAdmin)
admin.site.register(CmUf, CmUfAdmin)

admin.site.register(EdCampo, EdCampoAdmin)
admin.site.register(EdCota, EdCotaAdmin)
admin.site.register(EdEdital, EdEditalAdmin)
admin.site.register(EdEditalPessoa, EdEditalPessoaAdmin)
admin.site.register(EdPessoaFormacao, EdPessoaFormacaoAdmin)
admin.site.register(EdPessoaVagaCampoCheckbox, EdPessoaVagaCampoCheckboxAdmin)
admin.site.register(EdPessoaVagaCampoCombobox, EdPessoaVagaCampoComboboxAdmin)
admin.site.register(EdPessoaVagaCampoDatebox, EdPessoaVagaCampoDateboxAdmin)
admin.site.register(
    EdPessoaVagaCampoCheckboxUpload, EdPessoaVagaCampoCheckboxUploadAdmin
)
admin.site.register(
    EdPessoaVagaCampoComboboxUpload, EdPessoaVagaCampoComboboxUploadAdmin
)
admin.site.register(EdPessoaVagaCampoDateboxUpload, EdPessoaVagaCampoDateboxUploadAdmin)
admin.site.register(EdPessoaVagaConfirmacao, EdPessoaVagaConfirmacaoAdmin)
admin.site.register(EdPessoaVagaCota, EdPessoaVagaCotaAdmin)
admin.site.register(EdPessoaVagaInscricao, EdPessoaVagaInscricaoAdmin)
admin.site.register(EdPessoaVagaJustificativa, EdPessoaVagaJustificativaAdmin)
admin.site.register(EdPessoaVagaValidacao, EdPessoaVagaValidacaoAdmin)
admin.site.register(EdUnidade, EdUnidadeAdmin)
admin.site.register(EdVaga, EdVagaAdmin)
admin.site.register(EdVagaCota, EdVagaCotaAdmin)
admin.site.register(EdVagaCampoCheckbox, EdVagaCampoCheckboxAdmin)
admin.site.register(EdVagaCampoCombobox, EdVagaCampoComboboxAdmin)
admin.site.register(EdVagaCampoDatebox, EdVagaCampoDateboxAdmin)

admin.site.register(FiDatafrequencia, FiDataFrequenciaAdmin)
admin.site.register(FiFrequencia, FiFrequenciaAdmin)
admin.site.register(FiFuncaoBolsista, FiFuncaoBolsistaAdmin)
admin.site.register(FiPessoaFicha, FiPessoaFichaAdmin)
admin.site.register(FiFrequenciaDisciplina, FiFrequenciaDisciplinaAdmin)

admin.site.register(TrTermo, TrTermoAdmin)
admin.site.register(TrEspacoFisico, TrEspacoFisicoAdmin)
admin.site.register(TrDisponibilidadeEquipe, TrDisponibilidadeEquipeAdmin)
admin.site.register(TrIndisponibilidadeEquipe, TrIndisponibilidadeEquipeAdmin)
admin.site.register(TrTransmissao, TrTransmissaoAdmin)
admin.site.register(TrTransmissaoEmail, TrTransmissaoEmailAdmin)
admin.site.register(TrTransmissaoRecusada, TrTransmissaoRecusadaAdmin)
admin.site.register(TrLimites, TrLimitesAdmin)
