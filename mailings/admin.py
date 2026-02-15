from django.contrib import admin
from django.contrib import messages
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
    list_display = ('id', 'get_status_display', 'start_time', 'end_time', 'message')
    list_filter = ('status', 'start_time', 'end_time')
    search_fields = ('message__subject',)
    filter_horizontal = ('recipients',)
    actions = ['send_mailing_action']

    def get_status_display(self, obj):
        """Отображение динамического статуса"""
        return obj.get_current_status()
    get_status_display.short_description = 'Статус'

    def get_object(self, request, object_id, from_field=None):
        """Обновление статуса при просмотре объекта"""
        obj = super().get_object(request, object_id, from_field)
        if obj:
            obj.update_status()
        return obj

    def send_mailing_action(self, request, queryset):
        """Отправка рассылки через админ-панель"""
        from .services import send_mailing

        success_count = 0
        error_count = 0

        for mailing in queryset:
            result = send_mailing(mailing.id)
            if result['success']:
                success_count += 1
            else:
                error_count += 1
                messages.warning(request, f"Рассылка {mailing.id}: {result['message']}")

        if success_count > 0:
            messages.success(request, f'Успешно отправлено рассылок: {success_count}')
        if error_count > 0:
            messages.error(request, f'Ошибок при отправке: {error_count}')

    send_mailing_action.short_description = 'Отправить выбранные рассылки'


@admin.register(MailingAttempt)
class MailingAttemptAdmin(admin.ModelAdmin):
    list_display = ('id', 'mailing', 'attempt_time', 'status', 'server_response')
    list_filter = ('status', 'attempt_time')
    search_fields = ('mailing__id', 'server_response')
    readonly_fields = ('mailing', 'attempt_time', 'status', 'server_response')
