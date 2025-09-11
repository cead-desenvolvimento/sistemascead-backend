from django.urls import path
from . import views

urlpatterns = [
    # Helpers na edicao da ficha pelo financeiro
    path("bolsista/editais/", views.ListarEditaisAPIView.as_view()),
    path("bolsista/funcoes/", views.ListarFuncoesAPIView.as_view()),
    path("bolsista/ofertas/", views.ListarOfertasAPIView.as_view()),
    path(
        "bolsistas/",
        views.ListarUltimasFichasAPIView.as_view(),
        name="lista_ultimas_fichas",
    ),
    path(
        "bolsistas/ativos/",
        views.ListarCursosComBolsistasAtivosAPIView.as_view(),
        name="lista_cursos_com_bolsistas_ativos",
    ),
    path(
        "bolsistas/inativos/",
        views.ListarCursosComBolsistasInativosAPIView.as_view(),
        name="lista_cursos_com_bolsistas_inativos",
    ),
    path(
        "bolsistas/ativos/<int:ac_curso_id>/",
        views.CursoComBolsistasAtivosAPIView.as_view(),
        name="curso_com_bolsistas_ativos",
    ),
    path(
        "bolsistas/inativos/<int:ac_curso_id>/",
        views.CursoComBolsistasInativosAPIView.as_view(),
        name="curso_com_bolsistas_inativos",
    ),
    path(
        "bolsista/atualizar/",
        views.AtualizarDataVinculoBolsistaAPIView.as_view(),
        name="atualizar_data_vinculo_bolsista",
    ),
    path(
        "bolsista/atualizar_ficha/",
        views.AtualizarFiPessoaFichaAPIView.as_view(),
        name="atualizar_ficha",
    ),
    path(
        "bolsista/ficha/<int:ficha_id>/",
        views.DetalharFiPessoaFichaAPIView.as_view(),
        name="detalhar_ficha",
    ),
    path(
        "bolsista/buscar/",
        views.ListarFiPessoaFichaPorNomeOuCpfAPIView.as_view(),
        name="buscar_bolsista",
    ),
    # Para associar editais, funcao da ficha e oferta
    path(
        "listar_editais_atuais/",
        views.ListarEditaisAtuaisAPIView.as_view(),
        name="listar_editais_atuais",
    ),
    path(
        "listar_ofertas_atuais/",
        views.ListarOfertasAtuaisAPIView.as_view(),
        name="listar_ofertas_atuais",
    ),
    path(
        "listar_funcoes_com_ficha_uab/",
        views.ListarFuncoesComFichaUABAPIView.as_view(),
        name="listar_funcoes_com_ficha_uab",
    ),
    path(
        "associar_edital_funcao_oferta/",
        views.AssociarEditalFuncaoFichaOfertaAPIView.as_view(),
        name="associar_edital_funcao_oferta",
    ),
    path(
        "associar_edital_funcao_oferta/id/<int:id>/",
        views.AssociarEditalFuncaoFichaOfertaRetrieveDestroyAPIView.as_view(),
        name="associar_edital_funcao_oferta_detalhe",
    ),
]
