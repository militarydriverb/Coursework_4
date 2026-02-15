from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('email', 'username', 'role', 'is_blocked', 'email_verified', 'is_staff')
    list_filter = ('role', 'is_blocked', 'email_verified', 'is_staff', 'is_superuser')
    search_fields = ('email', 'username')

    fieldsets = BaseUserAdmin.fieldsets + (
        ('Дополнительная информация', {
            'fields': ('role', 'is_blocked', 'email_verified', 'verification_token')
        }),
    )

    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Дополнительная информация', {
            'fields': ('email', 'role', 'is_blocked', 'email_verified')
        }),
    )

    actions = ['block_users', 'unblock_users']

    def block_users(self, request, queryset):
        """Блокировка пользователей"""
        count = queryset.update(is_blocked=True)
        self.message_user(request, f'Заблокировано пользователей: {count}')
    block_users.short_description = 'Заблокировать выбранных пользователей'

    def unblock_users(self, request, queryset):
        """Разблокировка пользователей"""
        count = queryset.update(is_blocked=False)
        self.message_user(request, f'Разблокировано пользователей: {count}')
    unblock_users.short_description = 'Разблокировать выбранных пользователей'
