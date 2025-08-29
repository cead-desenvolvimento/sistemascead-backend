from django.urls import path
from . import views

urlpatterns = [
    # Em ordem do fluxo da inscricao
    path("editais/", views.EditaisFaseInscricaoView.as_view(), name="editais"),
    path(
        "edital/<int:ano>/<int:numero>/",
        views.VagasEditalFaseInscricaoView.as_view(),
        name="listar_vagas",
    ),
    path("consultar_pessoa/", views.ValidarCPFView.as_view(), name="consultar_pessoa"),
    path("criar_pessoa/", views.CriarPessoaView.as_view(), name="criar_pessoa"),
    path(
        "enviar_codigo_email/",
        views.EnviarCodigoEmailView.as_view(),
        name="enviar_codigo_email",
    ),
    path(
        "verificar_codigo_email/",
        views.VerificarCodigoView.as_view(),
        name="verificar_codigo_email",
    ),
    path("cota/", views.AssociarPessoaVagaCotaView.as_view(), name="cota"),  # get/post
    path(
        "cota/<int:cota_id>/",
        views.AssociarPessoaVagaCotaView.as_view(),
        name="apagar_cota",
    ),  # delete
    path(
        "alerta_inscricao/",
        views.AlertaInscricaoView.as_view(),
        name="alerta_inscricao",
    ),
    path(
        "listar_pessoa_formacao/",
        views.ListarPessoaFormacaoView.as_view(),
        name="listar_pessoa_formacao",
    ),  # get/post
    path(
        "listar_pessoa_formacao/<int:formacao_id>/",
        views.ListarPessoaFormacaoView.as_view(),
        name="apagar_formacao",
    ),  # delete
    path(
        "listar_formacao/", views.ListarFormacaoView.as_view(), name="listar_formacao"
    ),
    path("vaga_campo/", views.VagaCamposView.as_view(), name="vaga_campo"),
    path(
        "pessoa_vaga_campo/",
        views.PessoaVagaCampoView.as_view(),
        name="pessoa_vaga_campo",
    ),
    path(
        "baixar_arquivo_inscricao/",
        views.BaixarArquivoInscricaoView.as_view(),
        name="baixar_arquivo_inscricao",
    ),
    path(
        "anexar_arquivos/", views.AnexarArquivosView.as_view(), name="anexar_arquivos"
    ),
    path(
        "finalizar_inscricao/",
        views.FinalizarInscricaoView.as_view(),
        name="finalizar_inscricao",
    ),
    path("obter_inscricao/", views.GetInscricaoView.as_view(), name="obter_inscricao"),
]
