from django import forms
from django.forms.widgets import SplitDateTimeWidget

from .models import (
    EdEdital,
    EdVagaCampoDatebox,
    EdVagaCampoCheckbox,
    EdVagaCampoCombobox,
    TrEspacoFisico,
)


class EdEditalAdminForm(forms.ModelForm):
    class Meta:
        model = EdEdital
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        horas_padrao = {
            "data_inicio_inscricao": "00:00:00",
            "data_inicio_validacao": "00:00:00",
            "data_fim_inscricao": "16:00:00",
            "data_fim_validacao": "23:59:59",
            "data_validade": "00:00:00",
        }
        for field_name, hora in horas_padrao.items():
            field = self.fields.get(field_name)
            if isinstance(field.widget, SplitDateTimeWidget):
                field.widget.widgets[0].attrs.update({"placeholder": "Data"})
                field.widget.widgets[1].attrs.update(
                    {"value": hora, "placeholder": "hh:mm:ss"}
                )


class EdVagaCampoDateboxForm(forms.ModelForm):
    class Meta:
        model = EdVagaCampoDatebox
        fields = "__all__"

    def clean_fracao_pontuacao(self):
        valor = self.cleaned_data.get("fracao_pontuacao")
        return None if valor == 0 else valor

    def clean_multiplicador_fracao_pontuacao(self):
        valor = self.cleaned_data.get("multiplicador_fracao_pontuacao")
        return None if valor == 0 else valor

    def clean_pontuacao_maxima(self):
        valor = self.cleaned_data.get("pontuacao_maxima")
        return None if valor == 0 else valor


class EdVagaCampoCheckboxForm(forms.ModelForm):
    class Meta:
        model = EdVagaCampoCheckbox
        fields = "__all__"

    def clean_pontuacao(self):
        valor = self.cleaned_data.get("pontuacao")
        return None if valor == 0 else valor


class EdVagaCampoComboboxForm(forms.ModelForm):
    class Meta:
        model = EdVagaCampoCombobox
        fields = "__all__"

    def clean_pontuacao(self):
        valor = self.cleaned_data.get("pontuacao")
        return None if valor == 0 else valor


class TrEspacoFisicoForm(forms.ModelForm):
    class Meta:
        model = TrEspacoFisico
        fields = "__all__"

    def clean_dias_pre_transmissao(self):
        valor = self.cleaned_data.get("dias_pre_transmissao")
        return None if valor == 0 else valor

    def clean_dias_pos_transmissao(self):
        valor = self.cleaned_data.get("dias_pos_transmissao")
        return None if valor == 0 else valor
