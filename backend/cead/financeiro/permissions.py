from rest_framework import permissions
from rest_framework.exceptions import PermissionDenied

from .messages import (
    ERRO_FINANCEIRO_NAO_ESTA_NO_GRUPO_DE_ASSOCIADOR_VAGA_FICHA,
    ERRO_FINANCEIRO_NAO_ESTA_NO_GRUPO_DE_GERENCIADORES_VINCULACAO_FICHAS,
)


class IsGerenciadorVinculacaoFichas(permissions.BasePermission):
    message = ERRO_FINANCEIRO_NAO_ESTA_NO_GRUPO_DE_GERENCIADORES_VINCULACAO_FICHAS

    def has_permission(self, request, view):
        if (
            request.user
            and request.user.groups.filter(
                name__in=[
                    "Gerenciadores de vinculação de fichas",
                    "Financeiro - administradores",
                ]
            ).exists()
        ):
            return True
        raise PermissionDenied(detail=self.message)


class IsAssociadorEditalFuncaoFichaOferta(permissions.BasePermission):
    message = ERRO_FINANCEIRO_NAO_ESTA_NO_GRUPO_DE_ASSOCIADOR_VAGA_FICHA

    def has_permission(self, request, view):
        if (
            request.user
            and request.user.groups.filter(
                name__in=[
                    "Associadores de edital, função da ficha e oferta",
                    "Financeiro - administradores",
                ]
            ).exists()
        ):
            return True
        raise PermissionDenied(detail=self.message)
