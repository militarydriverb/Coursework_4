from django.core.exceptions import PermissionDenied


def check_owner_permission(user, obj):
    """Проверка, является ли пользователь владельцем объекта"""
    if user.is_superuser:
        return True
    if hasattr(obj, 'owner'):
        return obj.owner == user
    return False


def check_manager_or_owner(user, obj=None):
    """Проверка, является ли пользователь менеджером или владельцем"""
    if user.is_superuser:
        return True
    if user.is_manager():
        return True
    if obj and hasattr(obj, 'owner'):
        return obj.owner == user
    return False


class UserPermissionMixin:
    """Mixin для проверки прав доступа пользователей"""

    def get_queryset(self):
        """Фильтрация queryset по владельцу"""
        queryset = super().get_queryset()
        user = self.request.user

        if user.is_superuser:
            return queryset

        if user.is_manager():
            # Менеджеры видят все
            return queryset

        # Обычные пользователи видят только свои объекты
        if hasattr(queryset.model, 'owner'):
            return queryset.filter(owner=user)

        return queryset

    def has_change_permission(self, request, obj=None):
        """Проверка прав на изменение"""
        if request.user.is_superuser:
            return True

        if obj is None:
            return True

        # Менеджеры могут только просматривать
        if request.user.is_manager():
            return False

        # Владелец может изменять
        return check_owner_permission(request.user, obj)

    def has_delete_permission(self, request, obj=None):
        """Проверка прав на удаление"""
        if request.user.is_superuser:
            return True

        if obj is None:
            return True

        # Менеджеры не могут удалять
        if request.user.is_manager():
            return False

        # Владелец может удалять
        return check_owner_permission(request.user, obj)

    def save_model(self, request, obj, form, change):
        """Автоматическая установка владельца при создании"""
        if not change and hasattr(obj, 'owner'):
            obj.owner = request.user
        super().save_model(request, obj, form, change)
