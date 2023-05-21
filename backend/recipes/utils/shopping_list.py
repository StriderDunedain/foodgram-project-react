from django.db.models import F, Sum
from recipes.models import RecipeIngredient


def get_list_ingredients(user):
    ingredients = RecipeIngredient.objects.filter(
        recipe__shopping_recipe__user=user).values(
        name=F('ingredient__name'),
        measurement_unit=F('ingredient__measurement_unit')
    ).annotate(quantity=Sum('amount')).values_list(
        'ingredient__name', 'quantity', 'ingredient__measurement_unit')
    return ingredients
