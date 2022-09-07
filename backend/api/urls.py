from django.urls import include, path
from recipes.views import (FavoriteViewSet, IngredientViewSet, RecipeViewSet,
                           ShopingCartViewSet, TagViewSet)
from rest_framework.routers import DefaultRouter
from users.views import SubscriptionViewSet, UserViewSet

app_name = 'api'

router = DefaultRouter()
router.register('users', UserViewSet, basename='users')
router.register('tags', TagViewSet, basename='tags')
router.register('recipes', RecipeViewSet, basename='recipes')
router.register(
    r'recipes/(?P<id>\d+)/shopping_cart',
    ShopingCartViewSet,
    basename='shopping_cart'
)
router.register(
    r'recipes/(?P<id>\d+)/favorite',
    FavoriteViewSet,
    basename='favorite'
)
router.register(
    r'users/(?P<id>\d+)/subscribe',
    SubscriptionViewSet,
    basename='subscribe'
)
router.register('ingredients', IngredientViewSet, basename='ingredients')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('djoser.urls.authtoken')),
]
