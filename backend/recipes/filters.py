from django.db.models import Case, Value, When
from django_filters.rest_framework import (BooleanFilter, CharFilter,
                                           FilterSet,
                                           ModelMultipleChoiceFilter)

from .models import Ingredient, Recipe, Tag


class IngredientFilter(FilterSet):
    """Фильтр для выбора ингредиентов.
    Фильтрует по наименованию ингредиента (name) сначала по вхождению
    в начало наименования, затем по вхождению в произвользном месте."""

    name = CharFilter(method='name_filter')

    class Meta:
        model = Ingredient
        fields = ('name',)

    def name_filter(self, queryset, name, value):
        if not value:
            return queryset
        filtered_queryset = queryset.filter(name__icontains=value).annotate(
            order=Case(
                When(name__istartswith=value, then=Value(1)),
                default=Value(2)
            )
        )
        return filtered_queryset.order_by('order')


class RecipeFilter(FilterSet):
    """Фильтр рецептов.
    Фильтрует по наименованию (name), автору (author), тегам(tags),
    вхождению в корзину (is_in_shopping_cart) и избранное(is_favorited)."""

    tags = ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all(),
    )

    is_favorited = BooleanFilter(
        field_name='favorited',
        method='choice_filter',
    )
    is_in_shopping_cart = BooleanFilter(
        field_name='in_shopping_cart',
        method='choice_filter',
    )

    class Meta:
        model = Recipe
        fields = ('name', 'author', 'tags',)

    def choice_filter(self, queryset, name, value):
        if not value:
            return queryset
        kwargs = {
            name: self.request.user.id,
        }
        return queryset.filter(**kwargs)
