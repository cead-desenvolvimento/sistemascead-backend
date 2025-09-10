from django.conf import settings
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect, render

from drf_spectacular.utils import extend_schema
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from cead.models import DjUri

from .api_docs import *
from .messages import *
from .serializers import CustomTokenObtainPairSerializer, DjUriSerializer


class CustomLoginView(LoginView):
    template_name = "usuario/entrar.html"

    # Valida o login
    def form_valid(self, form):
        response = super().form_valid(form)
        user = self.request.user

        refresh = RefreshToken.for_user(user)

        return render(
            self.request,
            "usuario/redireciona.html",
            {
                "token": str(refresh.access_token),
                "refresh_token": str(refresh),
                "next_url": self.get_success_url() or "index.html",
            },
        )

    # Usa o redirect em settings.LOGIN_REDIRECT_URLS
    def get_success_url(self):
        next_url = self.request.GET.get("next")
        if next_url:
            return next_url

        current_path = self.request.path
        if current_path in settings.LOGIN_REDIRECT_URLS:
            return settings.LOGIN_REDIRECT_URLS[current_path]

        return settings.LOGIN_REDIRECT_URL


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


@login_required
def trocar_senha(request):
    if request.method == "POST":
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            # Importante para manter o usuário logado após a troca de senha
            update_session_auth_hash(request, user)
            messages.success(request, OK_SENHA_ALTERADA)
            return redirect("trocar_senha_sucesso")
        else:
            messages.error(request, ERRO_CORRIJA_ERROS)
    else:
        form = PasswordChangeForm(request.user)

    return render(request, "usuario/trocar_senha.html", {"form": form})


@login_required
def trocar_senha_sucesso(request):
    return render(request, "usuario/trocar_senha_sucesso.html")


@extend_schema(**DOCS_OBTER_URIS_PERMITIDAS)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def obter_uris_permitidas(request):
    grupos_usuario = request.user.groups.values_list("id", flat=True)
    uris_permitidas = (
        DjUri.objects.filter(djgrupouri__auth_group_id__in=grupos_usuario)
        .distinct()
        .order_by("uri")
    )
    serializer = DjUriSerializer(uris_permitidas, many=True)

    return Response({"is_staff": request.user.is_staff, "uris": serializer.data})
