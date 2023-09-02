from django_filters import rest_framework as filters
from rest_framework.filters import SearchFilter

from recipes.models import Recipe, Tag


class RecipeFilter(filters.FilterSet):
    is_in_shopping_cart = filters.BooleanFilter(
        method='get_is_in_shopping_cart'
    )
    is_favorited = filters.BooleanFilter(method='get_is_favorited')
    tags = filters.ModelMultipleChoiceFilter(
        queryset=Tag.objects.all(),
        field_name='tags__slug',
        to_field_name='slug'
    )

    class Meta:
        model = Recipe
        fields = (
            'tags',
            'author'
        )

    def get_is_in_shopping_cart(self, queryset, name, value):
        if value:
            return queryset.filter(cart_recipe__user=self.request.user)
        return queryset

    def get_is_favorited(self, queryset, name, value):
        if value:
            return queryset.filter(fav_recipe__user=self.request.user)
        return queryset


class IngredientFilter(SearchFilter):
    search_param = 'name'
