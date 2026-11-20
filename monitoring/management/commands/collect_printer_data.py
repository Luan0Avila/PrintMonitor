from django.core.management.base import BaseCommand, CommandError

from monitoring.services.collector import collect_printer_data
from printer.services.octoprint import OctoPrintError


class Command(BaseCommand):
    help = "Coleta e armazena dados da impressora via OctoPrint."

    def handle(self, *args, **options):
        try:
            data = collect_printer_data()

        except OctoPrintError as error:
            raise CommandError(
                f"Falha na comunicação com o OctoPrint: {error}"
            ) from error

        connection = data.get("connection", {})

        if not connection.get("connected"):
            self.stdout.write(
                self.style.WARNING(
                    "Servidor OctoPrint acessível, mas impressora desconectada."
                )
            )
            return

        printer = data.get("printer", {})
        job = data.get("job") or {}

        self.stdout.write(
            self.style.SUCCESS(f"Coleta realizada. Estado: {printer.get('state')}")
        )

        if job.get("file"):
            self.stdout.write(
                f"Arquivo: {job['file']} | Progresso: {job.get('progress')}%"
            )
