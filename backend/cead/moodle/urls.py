from django.urls import path
from . import views

urlpatterns = [
    path(
        "relatorio/",
        views.ListarFiDatafrequenciaAPIView.as_view(),
        name="listar_relatorio_moodle",
    ),
    path(
        "relatorio/selecao/<int:fi_datafrequencia_id>/",
        views.SelecaoCursosRelatorioMoodleAPIView.as_view(),
        name="relatorio_selecao_moodle",
    ),
    path(
        "relatorio/<int:fi_datafrequencia_id>/",
        views.RelatorioMoodleAPIView.as_view(),
        name="relatorio_moodle",
    ),
]
