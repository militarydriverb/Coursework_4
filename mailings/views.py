from django.shortcuts import render
from django.db.models import Count
from .models import Mailing, Recipient


def home(request):
    """Главная страница со статистикой"""
    total_mailings = Mailing.objects.count()
    active_mailings = Mailing.objects.filter(status='Запущена').count()
    unique_recipients = Recipient.objects.count()

    context = {
        'total_mailings': total_mailings,
        'active_mailings': active_mailings,
        'unique_recipients': unique_recipients,
    }

    return render(request, 'mailings/home.html', context)
