from django.core.mail import send_mail
from django.conf import settings
from .models import Mailing, MailingAttempt


def send_mailing(mailing_id):
    """
    Отправка рассылки по ID

    Args:
        mailing_id: ID рассылки
    """
    try:
        mailing = Mailing.objects.get(id=mailing_id)
        mailing.update_status()

        if mailing.status == 'Завершена':
            return

        recipients = mailing.recipients.all()
        message = mailing.message

        for recipient in recipients:
            try:
                send_mail(
                    subject=message.subject,
                    message=message.body,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[recipient.email],
                    fail_silently=False,
                )

                MailingAttempt.objects.create(
                    mailing=mailing,
                    status='Успешно',
                    server_response=f'Письмо успешно отправлено на {recipient.email}'
                )

            except Exception as e:
                MailingAttempt.objects.create(
                    mailing=mailing,
                    status='Не успешно',
                    server_response=str(e)
                )

        if mailing.status == 'Создана':
            mailing.status = 'Запущена'
            mailing.save()

    except Mailing.DoesNotExist:
        pass
