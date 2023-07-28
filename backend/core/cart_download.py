from django.conf import settings as django_settings
from rest_framework import status
from rest_framework.response import Response

from recipes.models import Cart, IngredientAmount


def cart_data_generation(request):
    cart = Cart.objects.filter(user=request.user)
    if not cart.exists():
        return Response(django_settings.NO_RECIPE_FOR_DONWLOAD,
                        status=status.HTTP_404_NOT_FOUND)
    recipes = []
    for item in cart:
        recipes.append(item.recipe)
    ingredients = {}
    for recipe in recipes:
        recipeingr = IngredientAmount.objects.filter(recipe=recipe)
        for item in recipeingr:
            ingredients[item.ingredient] = (
                ingredients.get(item.ingredient, 0) + int(item.amount)
            )
    data_for_download = []
    for ingredient in ingredients:
        data_for_download.append(
            (ingredient.name, f'({ingredient.measurement_unit})',
             ingredients[ingredient])
        )
    return data_for_download
