from rest_framework import permissions
from rest_framework.exceptions import PermissionDenied

from .messages import (
    ERRO_LANCA_FREQUENCIA_NAO_ESTA_NO_GRUPO_EDITORES_DISCIPLINAS,
    ERRO_LANCA_FREQUENCIA_NAO_ESTA_NO_GRUPO_LANCADORES_DE_FREQUENCIA,
    ERRO_LANCA_FREQUENCIA_NAO_ESTA_NO_GRUPO_VISUALIZADORES_DE_RELATORIO_FREQUENCIA,
)


class IsLancadorDeFrequencia(permissions.BasePermission):
    message = ERRO_LANCA_FREQUENCIA_NAO_ESTA_NO_GRUPO_LANCADORES_DE_FREQUENCIA

    def has_permission(self, request, view):
        if (
            request.user
            and request.user.groups.filter(name="Lançadores de frequência").exists()
        ):
            return True
        raise PermissionDenied(detail=self.message)


class IsVisualizadordeRelatorioFrequencia(permissions.BasePermission):
    message = (
        ERRO_LANCA_FREQUENCIA_NAO_ESTA_NO_GRUPO_VISUALIZADORES_DE_RELATORIO_FREQUENCIA
    )

    def has_permission(self, request, view):
        if (
            request.user
            and request.user.groups.filter(
                name__in=[
                    "Visualizadores de relatório de Frequência",
                    "Financeiro - administradores",
                ]
            ).exists()
        ):
            return True
        raise PermissionDenied(detail=self.message)


class IsEditorDisciplina(permissions.BasePermission):
    message = ERRO_LANCA_FREQUENCIA_NAO_ESTA_NO_GRUPO_EDITORES_DISCIPLINAS

    def has_permission(self, request, view):
        if (
            request.user
            and request.user.groups.filter(
                name__in=[
                    "Editores de disciplinas",
                    "Acadêmico - administradores",
                    "Financeiro - administradores",
                ]
            ).exists()
        ):
            return True
        raise PermissionDenied(detail=self.message)
