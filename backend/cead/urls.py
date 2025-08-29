"""cead URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import include, path
from cead.admin import CmPessoaAutocomplete
from cead.autenticacao.views import CustomTokenObtainPairView
from django.contrib.auth.views import LoginView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/token/", CustomTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/token/verify/", TokenVerifyView.as_view(), name="token_verify"),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/docs/swagger/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path(
        "api/docs/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"
    ),
    path(
        "cm-pessoa-autocomplete/",
        CmPessoaAutocomplete.as_view(),
        name="cm_pessoa_autocomplete",
    ),
    path("autenticacao/", include("cead.autenticacao.urls")),
    path("editais/", include("cead.editais.urls")),
    path("ficha/", include("cead.ficha.urls")),
    path("financeiro/", include("cead.financeiro.urls")),
    path("lanca_frequencia/", include("cead.lanca_frequencia.urls")),
    path("inscricao/", include("cead.inscricao.urls")),
    path("moodle/", include("cead.moodle.urls")),
    path("transmissao/", include("cead.transmissao.urls")),
    path("wordpress/", include("cead.wordpress.urls")),
]
