from django.contrib.admin import ModelAdmin
from django.contrib.admin import register
from recipes.models import Recipe, Ingredient


@register(Recipe)
class RecipeAdmin(ModelAdmin):
    list_display = ('name', 'author')
    list_filter = (
        'author',
        'name',
        'tags',
        'count_favorites'
    )

    def count_recipes(self, obj):
        return obj.in_favorites.count()


@register(Ingredient)
class IngredientAdmin(ModelAdmin):
    list_display = ('name', 'measurement_unit')
    list_filter = ('name',)
