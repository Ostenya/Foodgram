from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Кастомная модель пользователя."""

    REQUIRED_FIELDS = [
        'password',
        'first_name',
        'last_name',
        'email',
    ]


class Subscription(models.Model):
    """Модель подписки одного пользователя (user) на другого (author)."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscriber',
        verbose_name='Подписчик',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscribed',
        verbose_name='Подписант',
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = "Подписки"
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_subscription',
            ),
        ]
