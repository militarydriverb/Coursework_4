from django.shortcuts import render
from django.utils import timezone
from .models import Mailing, Recipient


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
