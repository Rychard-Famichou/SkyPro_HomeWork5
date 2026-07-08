from django.core.management import BaseCommand, call_command


class Command(BaseCommand):
    help = "Загружает фикстуры"

    def handle(self, *args, **options):
        self.stdout.write(" Загрузка фикстур...")
        try:
            call_command("loaddata", "data_all_fixture.json")
            self.stdout.write(self.style.SUCCESS(" Фикстуры успешно загружены."))
        except Exception as e:
            self.stderr.write(
                self.style.WARNING(f" Не удалось загрузить фикстуры: {e}")
            )
