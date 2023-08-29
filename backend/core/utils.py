from django.db.models import Sum
from django.http import HttpResponse

from recipes.models import RecipeIngredient


def shopping_cart_util(user):
    items = RecipeIngredient.objects.filter(
        recipe__cart_recipe__user=user
    ).values(
        'ingredients__name',
        'ingredients__measurement_unit'
    ).annotate(
        total_amount=Sum('amount')
    ).order_by()
    shopping_list = ''
    for item in items:
        shopping_list += (f'{item["ingredients__name"]} '
                          f'({item["ingredients__measurement_unit"]}) - '
                          f'{item["total_amount"]} \n')

    response = HttpResponse(
        content=shopping_list,
        content_type='text/plain'
    )
    response['Content-Disposition'] = ('attachment; '
                                       'filename=shopping_cart.txt')
    return response
