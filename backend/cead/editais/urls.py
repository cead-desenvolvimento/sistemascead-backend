from django.urls import path
from . import views

urlpatterns = [
    # Auxiliares para envio de email
    path(
        "enviar_email/<str:email>/",
        views.EnviarEmailAPIView.as_view(),
        name="enviar_email",
    ),
    path("enviar_emails/", views.EnviarEmailsAPIView.as_view(), name="enviar_emails"),
    # Validacao
    path(
        "validar/",
        views.ListarEditaisValidacaoAPIView.as_view(),
        name="validar_editais",
    ),
    path(
        "validar/<int:ano>/<int:numero>/",
        views.ListarVagasValidacaoAPIView.as_view(),
        name="validar_edital",
    ),
    path(
        "validar/vaga/<int:vaga_id>/",
        views.ValidarVagaAPIView.as_view(),
        name="validar_vaga",
    ),
    path(
        "validar/verifica_validacao/<int:vaga_id>/<int:pessoa_id>/",
        views.VerificaValidacaoAPIView.as_view(),
        name="verifica_validacao",
    ),
    path(
        "validar/baixar_arquivo/",
        views.BaixarArquivosAPIView.as_view(),
        name="baixar_arquivo",
    ),
    # Envio de mensagem para preenchimento da ficha
    path(
        "enviar_mensagem/",
        views.ListarEditaisEmissoresMensagemFichaAPIView.as_view(),
        name="enviar_mensagem_editais",
    ),
    path(
        "enviar_mensagem/<int:ano>/<int:numero>/",
        views.ListarVagasEmissoresMensagemFichaAPIView.as_view(),
        name="enviar_mensagem_edital",
    ),
    path(
        "enviar_mensagem/vaga/<int:vaga_id>/",
        views.EmitirMensagemFichaVagaAPIView.as_view(),
        name="enviar_mensagem_vaga",
    ),
    # Relatorios
    path(
        "relatorio/listar/editais/",
        views.ListarEditaisRelatoriosAPIView.as_view(),
        name="relatorio_listar_editais",
    ),
    path(
        "relatorio/listar/edital/<int:ano>/<int:numero>/",
        views.ListarVagasRelatorioAPIView.as_view(),
        name="relatorio_listar_edital",
    ),
    path(
        "relatorio/edital/<int:ano>/<int:numero>/",
        views.RelatorioDoEditalAPIView.as_view(),
        name="relatorio_edital",
    ),
    path(
        "relatorio/vaga/<int:vaga_id>/",
        views.RelatorioDaVagaAPIView.as_view(),
        name="relatorio_vaga",
    ),
    # Associar edital com pessoa, para visualizacao dos editais pelos coordenadores
    path(
        "associar_edital_pessoa/",
        views.ListarEditaisAssociarEditalPessoaAPIView.as_view(),
        name="associar_edital_pessoa_lista",
    ),
    path(
        "associar_edital_pessoa/usuarios/",
        views.ListarPessoasParaAssociacaoAPIView.as_view(),
        name="associar_edital_pessoa_lista_usuarios",
    ),
    path(
        "associar_edital_pessoa/edital/<int:edital>/",
        views.AssociarEditalPessoaAPIView.as_view(),
        name="associar_edital_pessoa",
    ),
    path(
        "associar_edital_pessoa/<int:id>/",
        views.AssociarEditalPessoaRetrieveDestroyAPIView.as_view(),
        name="associar_edital_pessoa_detalhe",
    ),
    path(
        "usuario-por-cpf/<str:cpf>/",
        views.BuscarUsuarioPorCpfView.as_view(),
        name="usuario_por_cpf",
    ),
    # Justificativa
    path(
        "justificativa/",
        views.ListarEditalJustificativaAPIView.as_view(),
        name="listar-justificativa-edital",
    ),
    path(
        "<int:ano>/<int:numero>/justificativa/",
        views.EnviarJustificativaPorEmailAPIView.as_view(),
        name="enviar-justificativa-edital",
    ),
]
