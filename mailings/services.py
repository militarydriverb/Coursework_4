from django.core.mail import send_mail
from django.conf import settings
from .models import Mailing, MailingAttempt


def send_mailing(mailing_id):
    """
    Отправка рассылки по ID

    Args:
        mailing_id: ID рассылки

    Returns:
        dict: Результат отправки с информацией об успехе/ошибке
    """
    try:
        mailing = Mailing.objects.get(id=mailing_id)
        mailing.update_status()

        # Проверка: можно ли отправлять рассылку сейчас
        if not mailing.can_send():
            current_status = mailing.get_current_status()
            return {
                'success': False,
                'message': f'Рассылка не может быть отправлена. Текущий статус: {current_status}. '
                          f'Отправка возможна только между {mailing.start_time} и {mailing.end_time}.'
            }

        recipients = mailing.recipients.all()

        if not recipients.exists():
            return {
                'success': False,
                'message': 'У рассылки нет получателей.'
            }

        message = mailing.message
        success_count = 0
        error_count = 0

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
                success_count += 1

            except Exception as e:
                MailingAttempt.objects.create(
                    mailing=mailing,
                    status='Не успешно',
                    server_response=str(e)
                )
                error_count += 1

        # Обновляем статус после отправки
        mailing.update_status()

        return {
            'success': True,
            'message': f'Рассылка выполнена. Успешно: {success_count}, Ошибок: {error_count}',
            'success_count': success_count,
            'error_count': error_count
        }

    except Mailing.DoesNotExist:
        return {
            'success': False,
            'message': f'Рассылка с ID {mailing_id} не найдена.'
        }
