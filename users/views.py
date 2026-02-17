from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
import secrets
from .forms import RegisterForm, LoginForm, PasswordResetRequestForm, UserProfileForm
from .models import User


def register_view(request):
    """Регистрация пользователя"""
    if request.user.is_authenticated:
        return redirect('mailings:home')

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.email_verified = False
            user.verification_token = secrets.token_urlsafe(32)
            user.save()

            # Отправка письма с подтверждением
            verification_url = request.build_absolute_uri(
                reverse('users:verify_email', kwargs={'token': user.verification_token})
            )

            try:
                send_mail(
                    subject='Подтверждение email',
                    message=f'Для подтверждения email перейдите по ссылке: {verification_url}',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email],
                    fail_silently=False,
                )
                messages.success(request, 'Регистрация успешна! Проверьте email для подтверждения.')
            except Exception as e:
                messages.warning(request, f'Регистрация успешна, но не удалось отправить письмо: {e}')

            return redirect('users:login')
    else:
        form = RegisterForm()

    return render(request, 'users/register.html', {'form': form})


def login_view(request):
    """Вход пользователя"""
    if request.user.is_authenticated:
        return redirect('mailings:home')

    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')

            try:
                user = User.objects.get(email=email)
                user = authenticate(request, email=email, password=password)

                if user is not None:
                    if user.is_blocked:
                        messages.error(request, 'Ваш аккаунт заблокирован.')
                    elif not user.email_verified:
                        messages.warning(request, 'Пожалуйста, подтвердите ваш email.')
                    else:
                        login(request, user)
                        messages.success(request, f'Добро пожаловать, {user.email}!')
                        return redirect('mailings:home')
                else:
                    messages.error(request, 'Неверный email или пароль.')
            except User.DoesNotExist:
                messages.error(request, 'Пользователь с таким email не найден.')
    else:
        form = LoginForm()

    return render(request, 'users/login.html', {'form': form})


@login_required
def logout_view(request):
    """Выход пользователя"""
    logout(request)
    messages.success(request, 'Вы успешно вышли из системы.')
    return redirect('users:login')


def verify_email(request, token):
    """Подтверждение email"""
    try:
        user = User.objects.get(verification_token=token)
        user.email_verified = True
        user.verification_token = None
        user.save()
        messages.success(request, 'Email успешно подтвержден! Теперь вы можете войти.')
        return redirect('users:login')
    except User.DoesNotExist:
        messages.error(request, 'Неверная ссылка подтверждения.')
        return redirect('mailings:home')


def password_reset_request(request):
    """Запрос на восстановление пароля"""
    if request.method == 'POST':
        form = PasswordResetRequestForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            try:
                user = User.objects.get(email=email)
                reset_token = secrets.token_urlsafe(32)
                user.verification_token = reset_token
                user.save()

                reset_url = request.build_absolute_uri(
                    reverse('users:password_reset_confirm', kwargs={'token': reset_token})
                )

                send_mail(
                    subject='Восстановление пароля',
                    message=f'Для восстановления пароля перейдите по ссылке: {reset_url}',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email],
                    fail_silently=False,
                )
                messages.success(request, 'Инструкции по восстановлению пароля отправлены на ваш email.')
                return redirect('users:login')
            except User.DoesNotExist:
                messages.error(request, 'Пользователь с таким email не найден.')
    else:
        form = PasswordResetRequestForm()

    return render(request, 'users/password_reset_request.html', {'form': form})


def password_reset_confirm(request, token):
    """Подтверждение сброса пароля"""
    try:
        user = User.objects.get(verification_token=token)

        if request.method == 'POST':
            password1 = request.POST.get('password1')
            password2 = request.POST.get('password2')

            if password1 == password2:
                user.set_password(password1)
                user.verification_token = None
                user.save()
                messages.success(request, 'Пароль успешно изменен! Теперь вы можете войти.')
                return redirect('users:login')
            else:
                messages.error(request, 'Пароли не совпадают.')

        return render(request, 'users/password_reset_confirm.html', {'token': token})
    except User.DoesNotExist:
        messages.error(request, 'Неверная ссылка восстановления.')
        return redirect('users:login')


@login_required
def profile_view(request):
    """Просмотр профиля пользователя"""
    return render(request, 'users/profile.html', {'user': request.user})


@login_required
def profile_edit(request):
    """Редактирование профиля пользователя"""
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Профиль успешно обновлен!')
            return redirect('users:profile')
    else:
        form = UserProfileForm(instance=request.user)
    return render(request, 'users/profile_edit.html', {'form': form})
