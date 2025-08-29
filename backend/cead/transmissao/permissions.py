from rest_framework import permissions
from rest_framework.exceptions import PermissionDenied

from .messages import ERRO_TRANSMISSAO_NAO_ESTA_NO_GRUPO_REQUISITANTES_DE_TRANSMISSAO


class IsRequisitanteTransmissao(permissions.BasePermission):
    message = ERRO_TRANSMISSAO_NAO_ESTA_NO_GRUPO_REQUISITANTES_DE_TRANSMISSAO

    def has_permission(self, request, view):
        if (
            request.user
            and request.user.groups.filter(name="Requisitantes de transmissão").exists()
        ):
            return True
        raise PermissionDenied(detail=self.message)
