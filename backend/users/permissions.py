from rest_framework import permissions


class DetailsAuthenticatedOnly(permissions.BasePermission):
    """Доступ для вьюсета UserViewSet.
    Обеспечивает свободный доступ ко всем ресурсам, включая получение списка
    пользователей методом GET, регистрацию новых пользователей методом POST,
    изменение пароля пользователя методом POST,
    но доступ только авторизованных пользователей к получению детализированной
    информации о пользователе методом GET.
    """

    def has_permission(self, request, view):
        return True

    def has_object_permission(self, request, view, obj):
        return request.method != 'GET' or request.user.is_authenticated
