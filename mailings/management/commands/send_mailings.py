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
            try:
                mailing = Mailing.objects.get(id=mailing_id)
                send_mailing(mailing_id)
                self.stdout.write(
                    self.style.SUCCESS(f'Рассылка {mailing_id} успешно отправлена')
                )
            except Mailing.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'Рассылка с ID {mailing_id} не найдена')
                )
        else:
            mailings = Mailing.objects.exclude(status='Завершена')
            for mailing in mailings:
                send_mailing(mailing.id)
                self.stdout.write(
                    self.style.SUCCESS(f'Рассылка {mailing.id} отправлена')
                )
