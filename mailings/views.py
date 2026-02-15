from django.shortcuts import render
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_page
from django.core.cache import cache
from django.db.models import Count, Q
from .models import Mailing, Recipient, MailingAttempt


@cache_page(60 * 5)  # Кеш на 5 минут
def home(request):
    """Главная страница со статистикой"""
    # Обновляем статусы всех рассылок перед подсчетом
    all_mailings = Mailing.objects.all()
    for mailing in all_mailings:
        mailing.update_status()

    # Общее количество рассылок
    total_mailings = Mailing.objects.count()

    # Количество активных рассылок (статус 'Запущена')
    # Дополнительно проверяем, что текущее время между start_time и end_time
    now = timezone.now()
    active_mailings = Mailing.objects.filter(
        status='Запущена',
        start_time__lte=now,
        end_time__gte=now
    ).count()

    # Количество уникальных получателей
    unique_recipients = Recipient.objects.count()

    context = {
        'total_mailings': total_mailings,
        'active_mailings': active_mailings,
        'unique_recipients': unique_recipients,
    }

    return render(request, 'mailings/home.html', context)


@login_required
def user_statistics(request):
    """Статистика пользователя по его рассылкам"""
    user = request.user

    # Рассылки пользователя
    user_mailings = Mailing.objects.filter(owner=user)

    # Обновляем статусы
    for mailing in user_mailings:
        mailing.update_status()

    # Общее количество рассылок пользователя
    total_mailings = user_mailings.count()

    # Активные рассылки
    active_mailings = user_mailings.filter(status='Запущена', is_active=True).count()

    # Попытки рассылок пользователя
    user_attempts = MailingAttempt.objects.filter(mailing__owner=user)

    # Успешные попытки
    successful_attempts = user_attempts.filter(status='Успешно').count()

    # Неуспешные попытки
    failed_attempts = user_attempts.filter(status='Не успешно').count()

    # Всего попыток
    total_attempts = user_attempts.count()

    # Количество отправленных сообщений (успешных)
    total_sent_messages = successful_attempts

    # Получатели пользователя
    user_recipients = Recipient.objects.filter(owner=user).count()

    # Последние рассылки
    recent_mailings = user_mailings.order_by('-start_time')[:5]

    # Последние попытки
    recent_attempts = user_attempts.order_by('-attempt_time')[:10]

    context = {
        'total_mailings': total_mailings,
        'active_mailings': active_mailings,
        'successful_attempts': successful_attempts,
        'failed_attempts': failed_attempts,
        'total_attempts': total_attempts,
        'total_sent_messages': total_sent_messages,
        'user_recipients': user_recipients,
        'recent_mailings': recent_mailings,
        'recent_attempts': recent_attempts,
    }

    return render(request, 'mailings/statistics.html', context)
