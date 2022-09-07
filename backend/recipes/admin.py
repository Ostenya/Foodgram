from django.contrib import admin
from recipes.models import Ingredient, IngredientAmount, Recipe, Tag


class IngredientAmountInline(admin.TabularInline):
    model = IngredientAmount
    extra = 1
    verbose_name = 'Количество ингредиента'
    verbose_name_plural = "Количества ингредиентов"


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit',)
    search_fields = ('name',)
    list_filter = ('name',)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'slug',)
    search_fields = ('name',)
    list_filter = ('slug',)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'pub_date', 'get_favorited_number',)
    inlines = (IngredientAmountInline,)
    date_hierarchy = 'pub_date'
    search_fields = ('first_name', 'last_name',)
    list_filter = ('name', 'author', 'tags',)

    @staticmethod
    def get_favorited_number(obj):
        return obj.favorited.count()
