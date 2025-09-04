from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework.permissions import BasePermission

from cead.messages import (
    ERRO_GET_EDITAL,
)
from cead.models import (
    CmPessoa,
    EdEdital,
    EdEditalPessoa,
)

from .messages import (
    ERRO_GET_PESSOA,
    ERRO_NAO_ESTA_AUTORIZADO_A_VISUALIZAR_ESTE_RELATORIO,
    ERRO_NAO_ESTA_NO_GRUPO_ASSOCIADORES_DE_EDITAIS_PESSOAS,
    ERRO_NAO_ESTA_NO_GRUPO_EMISSORES_DE_MENSAGEM_FICHA,
    ERRO_NAO_ESTA_NO_GRUPO_VALIDADORES_DE_EDITAIS,
    ERRO_NAO_ESTA_NO_GRUPO_VISUALIZADORES_DE_RELATORIO_DE_EDITAIS,
)


class IsEmissorMensagemCriacaoFicha(BasePermission):
    message = ERRO_NAO_ESTA_NO_GRUPO_EMISSORES_DE_MENSAGEM_FICHA

    def has_permission(self, request, view):
        if (
            request.user
            and request.user.groups.filter(
                name__in=[
                    "Emissores de mensagem para criação de ficha",
                    "Acadêmico - administradores",
                    "Financeiro - administradores",
                ]
            ).exists()
        ):
            return True
        raise PermissionDenied(detail=self.message)


class IsValidadorDeEditais(BasePermission):
    message = ERRO_NAO_ESTA_NO_GRUPO_VALIDADORES_DE_EDITAIS

    def has_permission(self, request, view):
        if (
            request.user
            and request.user.groups.filter(
                name__in=[
                    "Validadores de editais",
                    "Acadêmico - administradores",
                ]
            ).exists()
        ):
            return True
        raise PermissionDenied(detail=self.message)


class IsAssociadorEditalPessoa(BasePermission):
    message = ERRO_NAO_ESTA_NO_GRUPO_ASSOCIADORES_DE_EDITAIS_PESSOAS

    def has_permission(self, request, view):
        if (
            request.user
            and request.user.groups.filter(
                name__in=[
                    "Associadores de editais e pessoas",
                    "Acadêmico - administradores",
                    "Financeiro - administradores",
                ]
            ).exists()
        ):
            return True
        raise PermissionDenied(detail=self.message)


class IsVisualizadordeRelatorioDeEditais(BasePermission):
    message = ERRO_NAO_ESTA_NO_GRUPO_VISUALIZADORES_DE_RELATORIO_DE_EDITAIS

    def has_permission(self, request, view):
        if (
            request.user
            and request.user.groups.filter(
                name__in=[
                    "Visualizadores de relatório de editais",
                    "Acadêmico - administradores",
                    "Financeiro - administradores",
                ]
            ).exists()
        ):
            return True
        raise PermissionDenied(detail=self.message)


class PodeAcessarEditalEspecifico(BasePermission):
    message = ERRO_NAO_ESTA_AUTORIZADO_A_VISUALIZAR_ESTE_RELATORIO

    def has_permission(self, request, view):
        # Administradores têm acesso total
        if request.user.groups.filter(name="Acadêmico - administradores").exists():
            return True

        # Para outros usuários, verificar se eles estão vinculados ao edital
        try:
            ano = view.kwargs.get("ano")
            numero = view.kwargs.get("numero")
            edital = EdEdital.objects.get(ano=ano, numero=numero)

            try:
                pessoa = CmPessoa.objects.get(cpf=request.user.username)
            except CmPessoa.DoesNotExist:
                raise PermissionDenied(detail=ERRO_GET_PESSOA)

            if EdEditalPessoa.objects.filter(
                cm_pessoa=pessoa, ed_edital=edital
            ).exists():
                return True

            raise PermissionDenied(detail=self.message)

        except EdEdital.DoesNotExist:
            raise NotFound(detail=ERRO_GET_EDITAL)
