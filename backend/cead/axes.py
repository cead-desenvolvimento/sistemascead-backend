# Número de tentativas de login falhas permitidas
AXES_FAILURE_LIMIT = 5 
# Tempo de bloqueio em horas
AXES_COOLOFF_TIME = 1
# Bloquear apenas por usuário (não por IP compartilhado)
AXES_ONLY_USER_FAILURES = True
AXES_LOCK_OUT_BY_COMBINATION_USER_AND_IP = False

# Ordem de precedência dos headers para identificar o IP real
AXES_META_PRECEDENCE_ORDER = [
    'HTTP_X_FORWARDED_FOR',  # repassado pelo Nginx
    'HTTP_X_REAL_IP',        # fallback
    'REMOTE_ADDR',           # último recurso
]

# Whitelist
AXES_NEVER_LOCKOUT_WHITELIST = True
AXES_IP_WHITELIST = [
    '10.0.0.0/8',
    '172.16.0.0/12',
    '200.17.0.0/16',
    '200.131.0.0/16',
]
