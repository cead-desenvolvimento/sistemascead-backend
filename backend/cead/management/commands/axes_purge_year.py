from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils.timezone import now
from django.db.models import Q

try:
    from axes.models import AccessAttempt, AccessLog
except Exception:
    AccessAttempt = AccessLog = None


class Command(BaseCommand):
    help = "Apaga logs do django-axes mais antigos que N dias (padrão: 365)."

    def add_arguments(self, parser):
        parser.add_argument("--days", type=int, default=365, help="Idade em dias")
        parser.add_argument(
            "--dry-run", action="store_true", help="Apenas contar, não apagar"
        )
        parser.add_argument(
            "--chunk", type=int, default=5000, help="Tamanho do lote para delete"
        )

    def handle(self, *args, **opts):
        if AccessAttempt is None:
            self.stderr.write("axes.models não encontrados.")
            return

        cutoff = now() - timedelta(days=opts["days"])
        dry = opts["dry_run"]
        chunk = opts["chunk"]

        # AccessAttempt: attempt_time
        qs_attempts = AccessAttempt.objects.filter(attempt_time__lt=cutoff)

        # AccessLog: usar logout_time quando existir, senão attempt_time
        qs_logs = (
            AccessLog.objects.filter(
                Q(logout_time__lt=cutoff) | Q(attempt_time__lt=cutoff)
            )
            if AccessLog is not None
            else None
        )

        # Contagem
        n_att = qs_attempts.count()
        n_log = qs_logs.count() if qs_logs is not None else 0
        self.stdout.write(f"Cutoff: {cutoff.isoformat()}")
        self.stdout.write(f"Candidates -> AccessAttempt: {n_att}, AccessLog: {n_log}")

        if dry:
            self.stdout.write("Dry-run: nada será apagado.")
            return

        # Deleta em lotes para evitar transações enormes
        deleted_att = 0
        while True:
            ids = list(qs_attempts.values_list("pk", flat=True)[:chunk])
            if not ids:
                break
            deleted_att += AccessAttempt.objects.filter(pk__in=ids).delete()[0]
            self.stdout.write(f"Apagados {deleted_att}/{n_att} AccessAttempt...")

        deleted_log = 0
        if qs_logs is not None:
            while True:
                ids = list(qs_logs.values_list("pk", flat=True)[:chunk])
                if not ids:
                    break
                deleted_log += AccessLog.objects.filter(pk__in=ids).delete()[0]
                self.stdout.write(f"Apagados {deleted_log}/{n_log} AccessLog...")

        self.stdout.write(
            self.style.SUCCESS(
                f"Concluído. Removidos {deleted_att} AccessAttempt e {deleted_log} AccessLog."
            )
        )
