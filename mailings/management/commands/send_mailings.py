from django.core.management.base import BaseCommand
from mailings.services import send_mailing
from mailings.models import Mailing


class Command(BaseCommand):
    help = 'Отправка рассылок вручную через командную строку'

    def add_arguments(self, parser):
        parser.add_argument(
            '--mailing_id',
            type=int,
            help='ID конкретной рассылки для отправки'
        )

    def handle(self, *args, **options):
        mailing_id = options.get('mailing_id')

        if mailing_id:
            # Отправка конкретной рассылки
            result = send_mailing(mailing_id)

            if result['success']:
                self.stdout.write(
                    self.style.SUCCESS(f'✓ {result["message"]}')
                )
            else:
                self.stdout.write(
                    self.style.ERROR(f'✗ {result["message"]}')
                )
        else:
            # Отправка всех активных рассылок
            mailings = Mailing.objects.exclude(status='Завершена')

            if not mailings.exists():
                self.stdout.write(
                    self.style.WARNING('Нет активных рассылок для отправки')
                )
                return

            total_sent = 0
            total_errors = 0

            for mailing in mailings:
                result = send_mailing(mailing.id)

                if result['success']:
                    self.stdout.write(
                        self.style.SUCCESS(f'✓ Рассылка {mailing.id}: {result["message"]}')
                    )
                    total_sent += 1
                else:
                    self.stdout.write(
                        self.style.ERROR(f'✗ Рассылка {mailing.id}: {result["message"]}')
                    )
                    total_errors += 1

            self.stdout.write(
                self.style.SUCCESS(f'\nИтого: Отправлено: {total_sent}, Ошибок: {total_errors}')
            )
