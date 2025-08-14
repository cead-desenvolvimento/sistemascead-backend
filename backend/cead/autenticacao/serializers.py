from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.exceptions import AuthenticationFailed
from rest_framework import serializers

from cead.models import DjUri

from .messages import ERRO_CREDENCIAIS_INVALIDAS


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        try:
            return super().validate(attrs)
        except AuthenticationFailed:
            raise AuthenticationFailed(ERRO_CREDENCIAIS_INVALIDAS)


class DjUriSerializer(serializers.ModelSerializer):
    class Meta:
        model = DjUri
        fields = ["uri", "descricao"]
