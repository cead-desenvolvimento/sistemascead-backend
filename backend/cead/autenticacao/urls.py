from django.contrib.auth import views as auth_views
from django.urls import path

from . import views
from .forms import CustomPasswordResetForm


urlpatterns = [
    path("entrar/", views.CustomLoginView.as_view(), name="login"),
    path(
        "obter-uris-permitidas/",
        views.obter_uris_permitidas,
        name="obter-uris-permitidas",
    ),
    path(
        "senha-redefinicao/",
        auth_views.PasswordResetView.as_view(
            template_name="usuario/senha_redefinicao.html",
            form_class=CustomPasswordResetForm,
            email_template_name="usuario/email/texto_redefinicao.txt",
        ),
        name="password_reset",
    ),
    path(
        "senha-redefinicao/enviado/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="usuario/senha_redefinicao_enviado.html"
        ),
        name="password_reset_done",
    ),
    path(
        "senha-redefinicao/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="usuario/senha_redefinicao_confirmar.html"
        ),
        name="password_reset_confirm",
    ),
    path(
        "senha-redefinicao/completo/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="usuario/senha_redefinicao_completo.html"
        ),
        name="password_reset_complete",
    ),
    path("trocar-senha/", views.trocar_senha, name="trocar_senha"),
    path(
        "trocar-senha/sucesso/", views.trocar_senha_sucesso, name="trocar_senha_sucesso"
    ),
]
