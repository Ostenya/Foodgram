import csv

from django.db.models import Sum
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from users.serializers import AddRemoveRecipeSerializer

from .filters import IngredientFilter, RecipeFilter
from .mixins import PostDeleteViewSet
from .models import Ingredient, IngredientAmount, Recipe, Tag
from .permissions import AuthorOrReadOnly
from .serializers import (IngredientSerializer, RecipePostSerializer,
                          RecipeSerializer, TagSerializer)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Обрабатывает запросы на ендпоинты /ingredients."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (permissions.AllowAny,)
    pagination_class = None
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Обрабатывает запросы на ендпоинты /tags."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (permissions.AllowAny,)
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    """Обрабатывает запросы на ендпоинты /recipes.
    Также обрабатывает запрос на скачивание корзины (списка покупок)
    (action download_shopping_cart_get)."""

    queryset = Recipe.objects.all()
    permission_classes = (AuthorOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.request.method in permissions.SAFE_METHODS:
            return RecipeSerializer
        return RecipePostSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        serializer.save(author=self.request.user)

    @action(
        methods=['get'],
        detail=False,
        url_path='download_shopping_cart',
    )
    def download_shopping_cart_get(self, request):
        ingredient_amounts = IngredientAmount.objects.filter(
            recipe__in=request.user.shopping_cart.all()).select_related(
                'ingredient')
        shopping_list = ingredient_amounts.values(
            'ingredient__name',
            'ingredient__measurement_unit',
        ).annotate(
            ingredient_amount=Sum('amount')
        ).values_list(
            'ingredient__name',
            'ingredient__measurement_unit',
            'ingredient_amount',
        )
        with open(
            'shopping_list.csv',
            'w',
            newline='',
            encoding='utf-8'
        ) as csvfile:
            writer = csv.writer(csvfile)
            for ingredient in shopping_list:
                writer.writerow(ingredient)
        return FileResponse(
            open('shopping_list.csv', 'rb'),
            content_type='text/plain'
        )


class ShopingCartViewSet(PostDeleteViewSet):
    """Включает/исключает рецепт в корзину (список покупок).
    Атрибут in_shopping_cart модели Recipes и соответствующий
    атрибут shopping_cart модели User."""

    serializer_class = AddRemoveRecipeSerializer

    def get_queryset(self):
        return self.request.user.shopping_cart

    def create(self, request, *args, **kwargs):
        recipe = get_object_or_404(
            Recipe,
            id=self.kwargs.get('id')
        )
        recipe.in_shopping_cart.add(request.user)
        recipe.save()
        serializer = self.get_serializer(recipe)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers
        )

    def delete(self, request, id):
        recipe = get_object_or_404(
            Recipe,
            id=id
        )
        recipe.in_shopping_cart.remove(request.user)
        recipe.save()
        return Response({}, status=status.HTTP_204_NO_CONTENT)


class FavoriteViewSet(PostDeleteViewSet):
    """Включает/исключает рецепт в избранное.
    Атрибут favorited модели Recipes и соответствующий
    атрибут favorites модели User."""

    serializer_class = AddRemoveRecipeSerializer

    def get_queryset(self):
        return self.request.user.favorites

    def create(self, request, *args, **kwargs):
        recipe = get_object_or_404(
            Recipe,
            id=self.kwargs.get('id')
        )
        recipe.favorited.add(request.user)
        recipe.save()
        serializer = self.get_serializer(recipe)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers
        )

    def delete(self, request, id):
        recipe = get_object_or_404(
            Recipe,
            id=id
        )
        recipe.favorited.remove(request.user)
        recipe.save()
        return Response({}, status=status.HTTP_204_NO_CONTENT)
