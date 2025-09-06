from django.urls import path
from . import views

urlpatterns = [
    path("", views.LancaFrequenciaAPIView.as_view(), name="lanca_frequencia"),
    path(
        "previa/",
        views.LancaFrequenciaPreviaAPIView.as_view(),
        name="previa_lanca_frequencia",
    ),
    path(
        "relatorio/",
        views.RelatorioLancamentoAPIView.as_view(),
        name="relatorio_lancamento",
    ),
    path(
        "relatorio_administrativo/",
        views.ListarFiDatafrequenciaAPIView.as_view(),
        name="lista_relatorio_administrativo_lancamento",
    ),
    path(
        "relatorio_administrativo/<int:fi_datafrequencia_id>/",
        views.RelatorioAdministrativoLancamentoAPIView.as_view(),
        name="relatorio_administrativo_lancamento",
    ),
    path(
        "cursos/",
        views.ListarCursosComDisciplinasAPIView.as_view(),
        name="lista_cursos_com_disciplinas",
    ),
    path(
        "curso/<int:ac_curso_id>/disciplinas/",
        views.DisciplinasCursoAPIView.as_view(),
        name="disciplinas_do_curso",
    ),
    path(
        "disciplina/<int:id>/",
        views.DisciplinasCursoRetrieveUpdateDestroyAPIView.as_view(),
        name="disciplina_do_curso",
    ),
]
