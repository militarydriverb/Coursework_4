from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse


class BlockedUserMiddleware:
    """Middleware для блокировки заблокированных пользователей"""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            if request.user.is_blocked:
                # Исключаем URL выхода
                if request.path != reverse('users:logout'):
                    messages.error(request, 'Ваш аккаунт заблокирован. Обратитесь к администратору.')
                    return redirect('users:logout')

        response = self.get_response(request)
        return response
