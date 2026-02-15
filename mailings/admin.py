from django.contrib import admin
from .models import Recipient, Message, Mailing, MailingAttempt


@admin.register(Recipient)
class RecipientAdmin(admin.ModelAdmin):
    list_display = ('email', 'full_name', 'comment')
    search_fields = ('email', 'full_name')
    list_filter = ('email',)


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('subject', 'body')
    search_fields = ('subject',)


@admin.register(Mailing)
class MailingAdmin(admin.ModelAdmin):
    list_display = ('id', 'status', 'start_datetime', 'end_datetime', 'message')
    list_filter = ('status', 'start_datetime', 'end_datetime')
    search_fields = ('message__subject',)
    filter_horizontal = ('recipients',)
    actions = ['send_mailing_action']

    def send_mailing_action(self, request, queryset):
        """Отправка рассылки через админ-панель"""
        from .services import send_mailing

        for mailing in queryset:
            send_mailing(mailing.id)

        self.message_user(request, f'Отправка {queryset.count()} рассылок инициирована.')

    send_mailing_action.short_description = 'Отправить выбранные рассылки'


@admin.register(MailingAttempt)
class MailingAttemptAdmin(admin.ModelAdmin):
    list_display = ('id', 'mailing', 'attempt_datetime', 'status', 'server_response')
    list_filter = ('status', 'attempt_datetime')
    search_fields = ('mailing__id', 'server_response')
    readonly_fields = ('mailing', 'attempt_datetime', 'status', 'server_response')
