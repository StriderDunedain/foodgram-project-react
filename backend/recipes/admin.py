from django.contrib.admin import ModelAdmin, register

from .models import Cart, Favorite, Ingredient, Recipe, Tag, RecipeIngredient


@register(Tag)
class TagAdmin(ModelAdmin):
    list_display = ('name', 'color', 'slug')


@register(Recipe)
class RecipeAdmin(ModelAdmin):
    list_display = ('name', 'author', 'in_favorites')
    search_filter = ('author', 'name', 'tags')

    def in_favorites(self, recipe):
        return recipe.fav_recipe.count()


@register(Ingredient)
class IngredientAdmin(ModelAdmin):
    list_display = ('name', 'measurement_unit')
    search_fields = ('name',)


@register(Cart)
class CartAdmin(ModelAdmin):
    list_display = ('user', 'recipe')


@register(Favorite)
class FavoriteAdmin(ModelAdmin):
    list_display = ('user', 'recipe')


@register(RecipeIngredient)
class RecipeIngredientAdmin(ModelAdmin):
    list_display = ('recipe', 'ingredients')
