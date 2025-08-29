from django.urls import path

from . import views

urlpatterns = [
    path(
        "cursos_ativos/<str:nome_polo>/",
        views.get_cursos_ativos_do_polo,
        name="get_cursos_ativos_do_polo",
    ),
    path(
        "curso/<str:nome_curso>/contato/",
        views.get_curso_contato,
        name="get_curso_contato",
    ),
    path(
        "curso/<str:nome_curso>/descricao-perfil-egresso/",
        views.get_curso_descricao_perfil_egresso,
        name="get_curso_descricao_perfil_egresso",
    ),
    path(
        "polos_ativos/<str:nome_curso>/",
        views.get_polos_ativos_do_curso,
        name="get_polos_ativos_do_curso",
    ),
    path("polos/", views.get_polos, name="get_polos"),
    path("polos/quantidade/", views.get_polos_quantidade, name="get_polos_quantidade"),
    path(
        "polo/com-oferta-ativa/<str:nome_polo>/",
        views.get_polo_nome_com_oferta_ativa,
        name="get_polo_nome_com_oferta_ativa",
    ),
    path(
        "polo/informacoes/", views.get_polos_informacoes, name="get_polos_informacoes"
    ),
    path("polo/<str:nome_polo>/", views.get_polo, name="get_polo"),
    path(
        "polo/<str:nome_polo>/apresentacao/",
        views.get_polo_apresentacao,
        name="get_polo_apresentacao",
    ),
    path(
        "polo/<str:nome_polo>/horario-funcionamento/",
        views.get_polo_horario_funcionamento,
        name="get_polo_horario_funcionamento",
    ),
]
