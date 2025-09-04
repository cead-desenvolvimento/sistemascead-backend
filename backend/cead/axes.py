from datetime import timedelta

# Limite de tentativas
AXES_FAILURE_LIMIT = 25

# Tempo de bloqueio
AXES_COOLOFF_TIME = timedelta(minutes=15)

# Definir como o IP do cliente é obtido
AXES_CLIENT_IP_CALLABLE = "cead.utils.axes_utils.get_real_ip"

# Travar só por usuário (não mistura IP + user)
AXES_LOCKOUT_PARAMETERS = ["username"]

# Whitelist
AXES_NEVER_LOCKOUT_WHITELIST = True
AXES_IP_WHITELIST = [
    "10.0.0.0/8",
    "172.16.0.0/12",
    "200.17.0.0/16",
    "200.131.0.0/16",
]
