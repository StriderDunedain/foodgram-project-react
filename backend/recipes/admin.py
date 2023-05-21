from django.contrib import admin

from .models import (
    FavoriteRecipe, Ingredient, Recipe, RecipeIngredient, ShoppingList, Tag,
)

admin.site.register(Ingredient)
admin.site.register(Tag)
admin.site.register(RecipeIngredient)
admin.site.register(Recipe)
admin.site.register(FavoriteRecipe)
admin.site.register(ShoppingList)
