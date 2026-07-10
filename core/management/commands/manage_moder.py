from django.contrib.auth.models import Group
from django.core.management import BaseCommand

from users.models import CustomUser


class Command(BaseCommand):
    help = 'Управление членством пользователя в группе "Модераторы"'

    def add_arguments(self, parser):
        parser.add_argument("email", type=str, help="Email пользователя")

        parser.add_argument(
            "--remove",
            action="store_true",
            help="Удалить пользователя из группы вместо добавления",
        )

    def handle(self, *args, **options):
        email = options["email"]
        remove_action = options["remove"]
        group_name = "Модераторы"

        if remove_action:
            try:
                moderator_group = Group.objects.get(name=group_name)
            except Group.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'Ошибка: Группа "{group_name}" не существует.'))
                return
        else:
            moderator_group, created = Group.objects.get_or_create(name=group_name)
            if created:
                self.stdout.write(self.style.WARNING(f'Группа "{group_name}" была создана.'))

        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"Ошибка: Пользователь с email {email} не найден."))
            return

        if remove_action:
            if moderator_group in user.groups.all():
                user.groups.remove(moderator_group)
                self.stdout.write(self.style.SUCCESS(f'Пользователь {email} удален из группы "{group_name}".'))
            else:
                self.stdout.write(self.style.WARNING(f'Пользователь {email} не состоял в группе "{group_name}".'))
        else:
            if moderator_group in user.groups.all():
                self.stdout.write(self.style.WARNING(f'Пользователь {email} уже находится в группе "{group_name}".'))
            else:
                user.groups.add(moderator_group)
                self.stdout.write(self.style.SUCCESS(f'Пользователь {email} добавлен в группу "{group_name}".'))
