from django.db.models import Max, Sum
from django.db.models.functions import Coalesce
from django.db.models import FloatField

from cead.models import (
    EdVagaCampoCheckbox,
    EdVagaCampoCombobox,
    EdVagaCampoDatebox,
)


def calcular_maximo_de_pontos(vaga):
    soma_checkbox = EdVagaCampoCheckbox.objects.filter(
        ed_vaga=vaga, pontuacao__isnull=False
    ).aggregate(total=Coalesce(Sum("pontuacao", output_field=FloatField()), 0.0))[
        "total"
    ]

    soma_combobox = (
        EdVagaCampoCombobox.objects.filter(ed_vaga=vaga, pontuacao__isnull=False)
        .values("ed_campo_id")
        .annotate(max_pontuacao=Max("pontuacao"))
        .aggregate(total=Coalesce(Sum("max_pontuacao", output_field=FloatField()), 0.0))
    )["total"]

    soma_datebox = EdVagaCampoDatebox.objects.filter(
        ed_vaga=vaga, pontuacao_maxima__isnull=False
    ).aggregate(
        total=Coalesce(Sum("pontuacao_maxima", output_field=FloatField()), 0.0)
    )[
        "total"
    ]

    return round(float(soma_checkbox + soma_combobox + soma_datebox), 2)
