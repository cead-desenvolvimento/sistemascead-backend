from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.contrib.auth.hashers import make_password
from django.db import transaction
import secrets
import string


class Command(BaseCommand):
    help = "Cria usuários a partir de uma lista de CPFs, gera senha aleatória e adiciona todos ao grupo id=3. Imprime csv: cpf,senha,status"

    def handle(self, *args, **options):
        # ==============================
        # Da resposta de:
        #
        # SELECT cm_pessoa.cpf FROM pr_edital_usuario JOIN
        # (SELECT id_edital FROM pr_edital ORDER BY id_edital DESC LIMIT 10) last10
        # ON pr_edital_usuario.id_edital = last10.id_edital JOIN cm_pessoa
        # ON pr_edital_usuario.id_pessoa = cm_pessoa.id_pessoa
        # UNION DISTINCT SELECT cm_pessoa.cpf FROM cm_pessoa JOIN cm_curso
        # ON cm_pessoa.id_pessoa = cm_curso.coordenador WHERE cm_curso.status = '1';
        #
        # Busca todos os coordenadores de cursos ativos e validadores de edital
        # dos ultimos 10 editais no banco antigo
        # ==============================
        cpfs = [
            "42242975749",
            "90497538687",
            "04170503481",
            "33826404149",
            "00758792638",
            "05492824678",
            "50345060687",
            "98749528653",
            "72704810753",
            "72144645949",
            "00730392686",
            "17085688831",
            "33294038615",
            "05028877610",
            "01228774625",
            "20918615615",
            "95793607668",
            "58249184653",
            "66999170649",
            "02271483980",
            "51442272600",
            "16077605840",
            "04536895663",
            "06370034622",
            "04325704620",
            "01175617628",
            "09959792609",
            "31914252845",
            "05428768924",
            "04143591600",
            "83756655768",
        ]

        def norm_cpf(s: str) -> str:
            return "".join(ch for ch in (s or "") if ch.isdigit())

        def gen_pwd(n: int = 12) -> str:
            # Letras + dígitos (sem símbolos, facilita envio por e-mail/WhatsApp)
            alphabet = string.ascii_letters + string.digits
            return "".join(secrets.choice(alphabet) for _ in range(n))

        User = get_user_model()
        username_field = getattr(User, "USERNAME_FIELD", "username")

        # Grupo alvo: id=3 (auth_group)
        try:
            group = Group.objects.get(pk=3)
        except Group.DoesNotExist:
            raise CommandError("Grupo id=3 não encontrado em auth_group.")

        self.stdout.write("cpf,senha,status")

        for raw in cpfs:
            cpf = norm_cpf(raw)
            if len(cpf) != 11:
                self.stdout.write(f"{raw},,cpf_invalido")
                continue

            filters = {username_field: cpf}
            user = User.objects.filter(**filters).first()

            if user:
                # já existe: adiciona ao grupo (se ainda não estiver)
                if not user.groups.filter(pk=group.pk).exists():
                    user.groups.add(group)
                self.stdout.write(f"{cpf},,ja_existe")
                continue

            # criar usuário novo
            pwd_plain = gen_pwd(12)
            pwd_hash = make_password(pwd_plain)

            data = {
                username_field: cpf,
                "password": pwd_hash,
                "is_active": True,
            }

            try:
                with transaction.atomic():
                    user = User.objects.create(**data)
                    user.groups.add(group)
                self.stdout.write(f"{cpf},{pwd_plain},criado")
            except Exception as e:
                self.stdout.write(f"{cpf},,erro:{e}")
