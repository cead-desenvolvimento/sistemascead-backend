from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import BasePermission

from .messages import ERRO_NAO_ESTA_NO_GRUPO_VISUALIZADORES_DE_RELATORIO_MOODLE


class IsVisualizadordeRelatorioMoodle(BasePermission):
    message = ERRO_NAO_ESTA_NO_GRUPO_VISUALIZADORES_DE_RELATORIO_MOODLE

    def has_permission(self, request, view):
        if (
            request.user
            and request.user.groups.filter(
                name__in=[
                    "Visualizadores de relatório Moodle",
                    "Financeiro - administradores",
                ]
            ).exists()
        ):
            return True
        raise PermissionDenied(detail=self.message)
