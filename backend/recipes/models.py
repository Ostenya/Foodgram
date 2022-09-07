from colorfield.fields import ColorField
from django.db import models
from users.models import User


class Ingredient(models.Model):
    """Модель ингредиента."""

    name = models.CharField(
        max_length=128,
        unique=True,
        verbose_name='Название'
    )
    measurement_unit = models.CharField(
        max_length=32,
        verbose_name='Единица измерения'
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('name',)


class Tag(models.Model):
    """Модель тега."""

    name = models.CharField(
        max_length=128,
        unique=True,
        verbose_name='Название'
    )
    color = ColorField(
        default='#FF0000',
        verbose_name='Цвет'
    )
    slug = models.SlugField(
        max_length=50,
        unique=True,
        verbose_name='Техническое имя'
    )

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'


class Recipe(models.Model):
    """Модель рецепта."""

    name = models.CharField(max_length=200, verbose_name='Название')
    text = models.TextField(blank=True, verbose_name='Описание')
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='recipes',
        verbose_name='Автор'
    )
    image = models.ImageField(
        verbose_name='Картинка',
        upload_to='recipes/',
        blank=True,
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления (мин)'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientAmount',
        verbose_name='Ингредиенты',
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Тэги',
    )
    favorited = models.ManyToManyField(
        User,
        related_name='favorites',
        verbose_name='В избранном',
        blank=True,
    )
    in_shopping_cart = models.ManyToManyField(
        User,
        related_name='shopping_cart',
        verbose_name='В корзине',
        blank=True,
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-pub_date',)
        constraints = [
            models.UniqueConstraint(
                fields=('name', 'author'),
                name='unique_author_recipe',
            )
        ]


class IngredientAmount(models.Model):
    """Модель количества ингредиента.
    Промежуточная модель для Many-to-Many связи модели рецепта (Recipe)
    с моделью ингредиента (Ingredient)."""

    amount = models.PositiveSmallIntegerField(verbose_name='Количество')
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.RESTRICT,
        verbose_name='Ингредиент'
    )

    class Meta:
        verbose_name = 'Количество ингредиента'
        verbose_name_plural = "Количества ингредиентов"
        constraints = [
            models.UniqueConstraint(
                fields=('recipe', 'ingredient'),
                name='unique_recipe_ingredient',
            )
        ]
