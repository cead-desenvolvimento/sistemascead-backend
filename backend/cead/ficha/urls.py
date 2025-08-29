from django.urls import path
from . import views

urlpatterns = [
    # Em ordem do fluxo
    path(
        "iniciar/<str:codigo>/",
        views.CPFCodigoPessoaValidacaoView.as_view(),
        name="iniciar",
    ),
    path(
        "endereco_telefone_dados_bancarios/",
        views.CadastroEnderecoTelefoneBancoView.as_view(),
        name="endereco_telefone_dados_bancarios",
    ),
    path(
        "dados_fi_pessoa_ficha/",
        views.CadastroFiPessoaFichaAPIView.as_view(),
        name="dados_fi_pessoa_ficha",
    ),
    path("gerar_pdf/", views.GerarFichaPDFAPIView.as_view(), name="gerar_pdf"),
    # Utilidades
    path(
        "listar_municipios/",
        views.ListarMunicipiosAPIView.as_view(),
        name="listar_municipios",
    ),
]
