from django.contrib import admin
from django.contrib import messages
from .models import Recipient, Message, Mailing, MailingAttempt
from .permissions import UserPermissionMixin


@admin.register(Recipient)
class RecipientAdmin(UserPermissionMixin, admin.ModelAdmin):
    list_display = ('email', 'full_name', 'comment', 'owner')
    search_fields = ('email', 'full_name')
    list_filter = ('owner',)

    def get_readonly_fields(self, request, obj=None):
        """Менеджеры не могут редактировать"""
        if request.user.is_manager() and not request.user.is_superuser:
            return [f.name for f in self.model._meta.fields]
        return super().get_readonly_fields(request, obj)


@admin.register(Message)
class MessageAdmin(UserPermissionMixin, admin.ModelAdmin):
    list_display = ('subject', 'body', 'owner')
    search_fields = ('subject',)
    list_filter = ('owner',)

    def get_readonly_fields(self, request, obj=None):
        """Менеджеры не могут редактировать"""
        if request.user.is_manager() and not request.user.is_superuser:
            return [f.name for f in self.model._meta.fields]
        return super().get_readonly_fields(request, obj)


@admin.register(Mailing)
class MailingAdmin(UserPermissionMixin, admin.ModelAdmin):
    list_display = ('id', 'get_status_display', 'start_time', 'end_time', 'message', 'is_active', 'owner')
    list_filter = ('status', 'start_time', 'end_time', 'is_active', 'owner')
    search_fields = ('message__subject',)
    filter_horizontal = ('recipients',)
    actions = ['send_mailing_action', 'disable_mailing_action', 'enable_mailing_action']

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

    def get_readonly_fields(self, request, obj=None):
        """Менеджеры не могут редактировать"""
        if request.user.is_manager() and not request.user.is_superuser:
            return [f.name for f in self.model._meta.fields]
        return super().get_readonly_fields(request, obj)

    def get_queryset(self, request):
        """Фильтрация по владельцу для пользователей"""
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        if request.user.is_manager():
            return qs  # Менеджеры видят все
        return qs.filter(owner=request.user)

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        """Фильтрация получателей по владельцу"""
        if db_field.name == "recipients":
            if not request.user.is_superuser:
                kwargs["queryset"] = Recipient.objects.filter(owner=request.user)
        return super().formfield_for_manytomany(db_field, request, **kwargs)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """Фильтрация сообщений по владельцу"""
        if db_field.name == "message":
            if not request.user.is_superuser:
                kwargs["queryset"] = Message.objects.filter(owner=request.user)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def send_mailing_action(self, request, queryset):
        """Отправка рассылки через админ-панель"""
        from .services import send_mailing

        # Менеджеры не могут отправлять
        if request.user.is_manager() and not request.user.is_superuser:
            messages.error(request, 'У вас нет прав на отправку рассылок.')
            return

        success_count = 0
        error_count = 0

        for mailing in queryset:
            # Проверка прав владения
            if not request.user.is_superuser and mailing.owner != request.user:
                messages.warning(request, f'Рассылка {mailing.id}: у вас нет прав на отправку.')
                continue

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

    def disable_mailing_action(self, request, queryset):
        """Отключение рассылок (доступно менеджерам)"""
        count = queryset.update(is_active=False)
        messages.success(request, f'Отключено рассылок: {count}')
    disable_mailing_action.short_description = 'Отключить выбранные рассылки'

    def enable_mailing_action(self, request, queryset):
        """Включение рассылок (доступно менеджерам)"""
        count = queryset.update(is_active=True)
        messages.success(request, f'Включено рассылок: {count}')
    enable_mailing_action.short_description = 'Включить выбранные рассылки'


@admin.register(MailingAttempt)
class MailingAttemptAdmin(admin.ModelAdmin):
    list_display = ('id', 'mailing', 'attempt_time', 'status', 'server_response')
    list_filter = ('status', 'attempt_time')
    search_fields = ('mailing__id', 'server_response')
    readonly_fields = ('mailing', 'attempt_time', 'status', 'server_response')

    def get_queryset(self, request):
        """Фильтрация по владельцу рассылки"""
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        if request.user.is_manager():
            return qs  # Менеджеры видят все попытки
        return qs.filter(mailing__owner=request.user)
