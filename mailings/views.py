from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_page
from django.core.cache import cache
from django.db.models import Count, Q
from django.contrib import messages
from .models import Mailing, Recipient, MailingAttempt, Message
from .forms import MessageForm, RecipientForm, MailingForm


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


# CRUD для Message
@login_required
def message_list(request):
    """Список сообщений пользователя"""
    messages_list = Message.objects.filter(owner=request.user).order_by('-id')
    return render(request, 'mailings/message_list.html', {'messages': messages_list})


@login_required
def message_detail(request, pk):
    """Детальный просмотр сообщения"""
    message = get_object_or_404(Message, pk=pk, owner=request.user)
    return render(request, 'mailings/message_detail.html', {'message': message})


@login_required
def message_create(request):
    """Создание сообщения"""
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.owner = request.user
            message.save()
            messages.success(request, 'Сообщение успешно создано!')
            return redirect('mailings:message_list')
    else:
        form = MessageForm()
    return render(request, 'mailings/message_form.html', {'form': form, 'title': 'Создать сообщение'})


@login_required
def message_update(request, pk):
    """Редактирование сообщения"""
    message = get_object_or_404(Message, pk=pk, owner=request.user)
    if request.method == 'POST':
        form = MessageForm(request.POST, instance=message)
        if form.is_valid():
            form.save()
            messages.success(request, 'Сообщение успешно обновлено!')
            return redirect('mailings:message_detail', pk=pk)
    else:
        form = MessageForm(instance=message)
    return render(request, 'mailings/message_form.html', {'form': form, 'title': 'Редактировать сообщение'})


@login_required
def message_delete(request, pk):
    """Удаление сообщения"""
    message = get_object_or_404(Message, pk=pk, owner=request.user)
    if request.method == 'POST':
        message.delete()
        messages.success(request, 'Сообщение успешно удалено!')
        return redirect('mailings:message_list')
    return render(request, 'mailings/message_confirm_delete.html', {'message': message})


# CRUD для Recipient
@login_required
def recipient_list(request):
    """Список получателей пользователя"""
    recipients = Recipient.objects.filter(owner=request.user).order_by('full_name')
    return render(request, 'mailings/recipient_list.html', {'recipients': recipients})


@login_required
def recipient_detail(request, pk):
    """Детальный просмотр получателя"""
    recipient = get_object_or_404(Recipient, pk=pk, owner=request.user)
    return render(request, 'mailings/recipient_detail.html', {'recipient': recipient})


@login_required
def recipient_create(request):
    """Создание получателя"""
    if request.method == 'POST':
        form = RecipientForm(request.POST)
        if form.is_valid():
            recipient = form.save(commit=False)
            recipient.owner = request.user
            recipient.save()
            messages.success(request, 'Получатель успешно создан!')
            return redirect('mailings:recipient_list')
    else:
        form = RecipientForm()
    return render(request, 'mailings/recipient_form.html', {'form': form, 'title': 'Добавить получателя'})


@login_required
def recipient_update(request, pk):
    """Редактирование получателя"""
    recipient = get_object_or_404(Recipient, pk=pk, owner=request.user)
    if request.method == 'POST':
        form = RecipientForm(request.POST, instance=recipient)
        if form.is_valid():
            form.save()
            messages.success(request, 'Получатель успешно обновлен!')
            return redirect('mailings:recipient_detail', pk=pk)
    else:
        form = RecipientForm(instance=recipient)
    return render(request, 'mailings/recipient_form.html', {'form': form, 'title': 'Редактировать получателя'})


@login_required
def recipient_delete(request, pk):
    """Удаление получателя"""
    recipient = get_object_or_404(Recipient, pk=pk, owner=request.user)
    if request.method == 'POST':
        recipient.delete()
        messages.success(request, 'Получатель успешно удален!')
        return redirect('mailings:recipient_list')
    return render(request, 'mailings/recipient_confirm_delete.html', {'recipient': recipient})


# CRUD для Mailing
@login_required
def mailing_list(request):
    """Список рассылок пользователя"""
    mailings_list = Mailing.objects.filter(owner=request.user).order_by('-start_time')
    for mailing in mailings_list:
        mailing.update_status()
    return render(request, 'mailings/mailing_list.html', {'mailings': mailings_list})


@login_required
def mailing_detail(request, pk):
    """Детальный просмотр рассылки"""
    mailing = get_object_or_404(Mailing, pk=pk, owner=request.user)
    mailing.update_status()
    attempts = mailing.attempts.all()[:10]
    return render(request, 'mailings/mailing_detail.html', {'mailing': mailing, 'attempts': attempts})


@login_required
def mailing_create(request):
    """Создание рассылки"""
    if request.method == 'POST':
        form = MailingForm(request.POST, user=request.user)
        if form.is_valid():
            mailing = form.save(commit=False)
            mailing.owner = request.user
            mailing.save()
            form.save_m2m()
            messages.success(request, 'Рассылка успешно создана!')
            return redirect('mailings:mailing_list')
    else:
        form = MailingForm(user=request.user)
    return render(request, 'mailings/mailing_form.html', {'form': form, 'title': 'Создать рассылку'})


@login_required
def mailing_update(request, pk):
    """Редактирование рассылки"""
    mailing = get_object_or_404(Mailing, pk=pk, owner=request.user)
    if request.method == 'POST':
        form = MailingForm(request.POST, instance=mailing, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Рассылка успешно обновлена!')
            return redirect('mailings:mailing_detail', pk=pk)
    else:
        form = MailingForm(instance=mailing, user=request.user)
    return render(request, 'mailings/mailing_form.html', {'form': form, 'title': 'Редактировать рассылку'})


@login_required
def mailing_delete(request, pk):
    """Удаление рассылки"""
    mailing = get_object_or_404(Mailing, pk=pk, owner=request.user)
    if request.method == 'POST':
        mailing.delete()
        messages.success(request, 'Рассылка успешно удалена!')
        return redirect('mailings:mailing_list')
    return render(request, 'mailings/mailing_confirm_delete.html', {'mailing': mailing})
