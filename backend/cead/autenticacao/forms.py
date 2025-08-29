from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import PasswordResetForm
from django.template.loader import render_to_string

from cead.models import CmPessoa

User = get_user_model()


class CustomPasswordResetForm(PasswordResetForm):
    def get_users(self, email):
        users = User._default_manager.filter(email__iexact=email, is_active=True)
        if users.exists():
            return users

        try:
            pessoa = CmPessoa.objects.get(email__iexact=email)
            user = User.objects.get(username=pessoa.cpf, is_active=True)

            if not user.email:
                user.email = email
                user.save(update_fields=["email"])

            return [user]
        except (CmPessoa.DoesNotExist, User.DoesNotExist):
            return []

    def send_mail(
        self,
        subject_template_name,
        email_template_name,
        context,
        from_email,
        to_email,
        html_email_template_name=None,
    ):
        user = context.get("user")
        cpf = getattr(user, "username", None)
        if cpf:
            try:
                pessoa = CmPessoa.objects.get(cpf=cpf)
                context["pessoa_nome"] = pessoa.nome
            except CmPessoa.DoesNotExist:
                context["pessoa_nome"] = user.get_username()
        else:
            context["pessoa_nome"] = user.get_username()

        subject = render_to_string(subject_template_name, context)
        subject = "".join(subject.splitlines())
        body = render_to_string(email_template_name, context)

        send_mail(subject, body, from_email, [to_email], html_message=None)
