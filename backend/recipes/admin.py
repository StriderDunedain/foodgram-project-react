from django.contrib.admin import ModelAdmin, display, register

from recipes.models import Ingredient, Recipe


@register(Recipe)
class RecipeAdmin(ModelAdmin):
    list_display = ('name', 'author', 'count_favorites')
    list_filter = (
        'author',
        'name',
        'tags'
    )

    @display(description='В избранном')
    def count_favorites(self, obj):
        return obj.in_favorites.count()


@register(Ingredient)
class IngredientAdmin(ModelAdmin):
    list_display = ('name', 'measurement_unit')
    list_filter = ('name',)
