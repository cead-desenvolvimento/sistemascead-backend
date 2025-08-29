from django.urls import path

from . import views

urlpatterns = [
    path(
        "termo/",
        views.TermoAPIView.as_view(),
        name="get_termo",
    ),
    path(
        "espaco_fisico/",
        views.EspacoFisicoAPIView.as_view(),
        name="get_espaco_fisico",
    ),
    path(
        "datas_disponiveis/",
        views.DatasDisponiveisAPIView.as_view(),
        name="datas_disponiveis",
    ),
    path(
        "datas_disponiveis_fim_validas/",
        views.DatasFimValidasAPIView.as_view(),
        name="datas_disponiveis_fim_validas",
    ),
    path(
        "horarios_disponiveis/",
        views.HorariosDisponiveisAPIView.as_view(),
        name="horarios_disponiveis",
    ),
    path(
        "confirmacao/",
        views.ConfirmacaoTransmissaoAPIView.as_view(),
        name="confirmacao",
    ),
]
