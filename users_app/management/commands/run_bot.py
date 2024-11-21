from django.core.management.base import BaseCommand

from users_app.telegram_bot import main


class Command(BaseCommand):
    help = 'Runs the Telegram bot'

    def handle(self, *args, **options):
        main()
