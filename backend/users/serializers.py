from django.contrib.auth.password_validation import validate_password
from django.db import transaction
from recipes.models import Recipe
from rest_framework import exceptions, serializers

from .models import User


class CurrentUserSerializer(serializers.ModelSerializer):
    """Сериализатор для модели пользователя."""

    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'password',
        )
        read_only_fields = ('id', 'is_subscribed',)
        extra_kwargs = {'password': {'write_only': True}}

    def get_is_subscribed(self, obj):
        current_user = self.context.get('request').user
        return (
            current_user.is_authenticated
            and current_user.subscribed.filter(user=current_user).exists()
        )

    @transaction.atomic
    def create(self, validated_data):
        raw_password = validated_data.pop('password')
        user_created = User(**validated_data)
        user_created.set_password(raw_password)
        user_created.save()
        return user_created


class UserSetPasswordSerializer(serializers.ModelSerializer):
    """Сериализатор для изменения пароля пользователя."""

    new_password = serializers.CharField(style={'input_type': 'password'})
    current_password = serializers.CharField(style={'input_type': 'password'})

    class Meta:
        model = User
        fields = (
            'new_password',
            'current_password',
        )

    def validate(self, attrs):
        current_user = self.context.get('request').user or self.user
        if not current_user.check_password(attrs['current_password']):
            raise exceptions.ValidationError('Текущий пароль указан неверно!')
        validate_password(attrs["new_password"], current_user)
        return super().validate(attrs)

    @transaction.atomic
    def create(self, validated_data):
        current_user = self.context.get('request').user or self.user
        current_user.set_password(validated_data['new_password'])
        return current_user


class AddRemoveRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для добавления/удаления рецепта пользователем.
    Используется в отношении корзины (shopping_cart), избранного (favorites)
    и подписок (subscriptions)."""

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time',)
        extra_kwargs = {
            'name': {'required': False},
            'cooking_time': {'required': False},
        }


class SubscriptionSerializer(CurrentUserSerializer):
    """Сериализатор для создания/удаления подписок на других пользователей.
    Также используется вьюфункцией UserViewSet для отображения
    списка подписчиков (action get_subscriptions)."""

    recipes = AddRemoveRecipeSerializer(many=True, read_only=True)
    recipes_count = serializers.IntegerField()

    class Meta(CurrentUserSerializer.Meta):
        fields = CurrentUserSerializer.Meta.fields + (
            'recipes',
            'recipes_count',
        )
        read_only_fields = CurrentUserSerializer.Meta.read_only_fields + (
            'recipes',
            'recipes_count',
        )
        extra_kwargs = {
            'username': {'required': False},
            'password': {'required': False,
                         'write_only': True}
        }
