from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Subscription, User


class FavoriteInline(admin.TabularInline):
    model = User.favorites.through
    extra = 1
    verbose_name = 'Избранный рецепт'
    verbose_name_plural = "Избранное"


class ShoppingCartInline(admin.StackedInline):
    model = User.shopping_cart.through
    extra = 1
    verbose_name = 'Рецепт в корзине'
    verbose_name_plural = "Корзина"


class SubscriptionInline(admin.TabularInline):
    model = Subscription
    fk_name = 'author'
    extra = 1
    verbose_name = 'Подписка'
    verbose_name_plural = "Подписки"


@admin.register(User)
class MyUserAdmin(UserAdmin):
    list_display = ('id', 'email', 'username', 'first_name', 'last_name',)
    inlines = (FavoriteInline, ShoppingCartInline, SubscriptionInline,)
    search_fields = ('first_name', 'last_name',)


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_username', 'author_username',)
    search_fields = ('user_username', 'author_username',)

    @staticmethod
    def user_username(obj):
        return obj.user.username

    @staticmethod
    def author_username(obj):
        return obj.author.username
