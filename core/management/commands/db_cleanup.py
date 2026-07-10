from django.core.management import BaseCommand, call_command


class Command(BaseCommand):
    help = "Очищает базу данных перед использованием фикстур"

    def handle(self, *args, **options):
        self.stdout.write("Удаление старых данных перед загрузкой...")
        try:
            call_command("flush", interactive=False, reset_sequences=True)
            self.stdout.write(self.style.SUCCESS("Данные успешно удалены."))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Ошибка очистки данных: {e}"))
            return
