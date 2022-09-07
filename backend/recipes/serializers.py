from django.db import transaction
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from users.serializers import CurrentUserSerializer

from .models import Ingredient, IngredientAmount, Recipe, Tag


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для модели ингредиентов."""

    class Meta:
        model = Ingredient
        fields = '__all__'


class IngredientAmountSerializer(serializers.ModelSerializer):
    """Вложенный сериализатор ингредиентов для создания и обновления рецептов.
    Используется в рамках сериализатора RecipeSerializer для обработки
    запросов (to_internal_value)."""

    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())

    class Meta:
        model = IngredientAmount
        fields = ('id', 'amount',)


class FullIngredientAmountSerializer(serializers.ModelSerializer):
    """Вложенный сериализатор ингредиентов для представления рецептов.
    Используется в рамках сериализатора RecipePostSerializer для представления
    результатов (to_representation)."""

    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.CharField(source='ingredient.name')
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit')

    class Meta:
        model = IngredientAmount
        fields = ('id', 'name', 'measurement_unit', 'amount',)


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для модели тегов."""

    class Meta:
        model = Tag
        fields = '__all__'


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для представления списка рецептов и деталей рецепта.
    Также используется в качестве представления (to_representation)
    при создании рецептов в рамках соответствующего сериализатора
    (RecipePostSerializer)."""

    tags = TagSerializer(read_only=True, many=True)
    author = CurrentUserSerializer(read_only=True)
    image = Base64ImageField()
    ingredients = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients', 'is_favorited',
                  'is_in_shopping_cart', 'name', 'image', 'text',
                  'cooking_time',)

    def get_ingredients(self, obj):
        return FullIngredientAmountSerializer(
            IngredientAmount.objects.filter(recipe=obj),
            many=True,
        ).data

    def get_is_favorited(self, obj):
        return obj.favorited.filter(
            id=self.context.get('request').user.id
        ).exists()

    def get_is_in_shopping_cart(self, obj):
        return obj.in_shopping_cart.filter(
            id=self.context.get('request').user.id
        ).exists()


class RecipePostSerializer(serializers.ModelSerializer):
    """Сериализатор для создания (create) и обновления (update) рецептов."""

    ingredients = IngredientAmountSerializer(many=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('ingredients', 'tags', 'image', 'name', 'text',
                  'cooking_time',)

    @staticmethod
    def ingredients_tags_create(instance, ingredients, tags):
        ingredients_list = []
        for ingredient in ingredients:
            ingredients_list.append(IngredientAmount(
                amount=ingredient['amount'],
                recipe=instance,
                ingredient=ingredient['id'],
            ))
        IngredientAmount.objects.bulk_create(ingredients_list)
        for tag in tags:
            instance.tags.add(tag)

    @transaction.atomic
    def create(self, validated_data):
        current_ingredients = validated_data.pop('ingredients')
        current_tags = validated_data.pop('tags')
        recipe_created = Recipe.objects.create(**validated_data)
        self.ingredients_tags_create(
            recipe_created,
            current_ingredients,
            current_tags,
        )
        recipe_created.save()
        return recipe_created

    @transaction.atomic
    def update(self, recipe_updated, validated_data):
        current_ingredients = validated_data.pop('ingredients')
        current_tags = validated_data.pop('tags')
        recipe_updated.ingredients.clear()
        recipe_updated.tags.clear()
        self.ingredients_tags_create(
            recipe_updated,
            current_ingredients,
            current_tags,
        )
        recipe_updated.save()
        return recipe_updated

    def to_representation(self, obj):
        return RecipeSerializer(
            obj,
            context={'request': self.context.get('request')},
        ).data
