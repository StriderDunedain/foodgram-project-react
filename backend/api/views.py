from django.db.models import Sum
from django.shortcuts import get_object_or_404
from rest_framework.mixins import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework.decorators import action
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_204_NO_CONTENT

from recipes.models import Ingredient, Recipe, Tag, Favorite, Cart, RecipeIngredient
from users.models import User, Subscription

from .pagination import RecipePagination
from .serializers import (IngredientSerializer, TagSerializer,
                          UserCreateSerializer, UserSerializer,
                          RecipeSerializer, SubscriptionSerializer,
                          RecipeDetailSerializer)


def common_post_method(model, kwargs, request):
    obj = get_object_or_404(model, pk=kwargs['pk'])
    user = request.user
    if model == Subscription:
        Subscription.objects.create(author=obj, subscriber=user)
        serializer = SubscriptionSerializer(obj)
        return Response(serializer.data, status=HTTP_201_CREATED)

    Favorite.objects.create(user=user, recipe=obj)
    serializer = RecipeDetailSerializer(obj)
    return Response(serializer.data, status=HTTP_201_CREATED)



class UserModelViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = RecipePagination

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return UserCreateSerializer
        return super().get_serializer_class()

    @action(detail=False, methods=['GET'])
    def subscriptions(self, request):
        user = request.user
        authors = User.objects.filter(subscriptions__subscriber=user)
        page = self.paginate_queryset(authors)
        serializer = SubscriptionSerializer(
            page,
            context={'request': request},
            many=True
        )
        return self.get_paginated_response(serializer.data)

    @action(detail=True, methods=['POST'])
    def subscribe(self, *args, **kwargs):
        author = get_object_or_404(User, pk=kwargs['pk'])
        user = self.request.user
        Subscription.objects.create(author=author, subscriber=user)
        serializer = SubscriptionSerializer(author)
        return Response(serializer.data, status=HTTP_201_CREATED)

    @subscribe.mapping.delete
    def delete_subscribe(self, *args, **kwargs):
        author = get_object_or_404(User, pk=kwargs['pk'])
        user = self.request.user
        author.subscriptions.filter(subscriber=user).delete()
        return Response(status=HTTP_204_NO_CONTENT)


class TagModelViewSet(ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientModelViewSet(ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer


class RecipeModelViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    pagination_class = RecipePagination

    @action(detail=False, methods=['GET'])
    def download_shopping_cart(self, request):
        user = request.user
        items = RecipeIngredient.objects.filter(
            recipe__cart_recipe__user=user
        ).values(
            'ingredients__name',
            'ingredients__measurement_unit'
        ).annotate(
            total_amount=Sum('amount')
        ).order_by()
        print(items)

        return Response({'sorry, not yet implemented': 1}, status=HTTP_200_OK)

    @action(detail=True, methods=['POST'])
    def shopping_cart(self, request, pk):
        recipe = get_object_or_404(Recipe, pk=pk)
        user = request.user
        Cart.objects.create(user=user, recipe=recipe)
        serializer = RecipeDetailSerializer(recipe)
        return Response(serializer.data, status=HTTP_201_CREATED)

    @shopping_cart.mapping.delete
    def delete_shopping_cart(self, *args, **kwargs):
        recipe = get_object_or_404(Recipe, pk=kwargs['pk'])
        user = self.request.user
        recipe.cart_recipe.filter(user=user).delete()
        return Response(status=HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['POST'])
    def favorite(self, request, pk):
        recipe = get_object_or_404(Recipe, pk=pk)
        user = request.user
        Favorite.objects.create(user=user, recipe=recipe)
        serializer = RecipeDetailSerializer(recipe)
        return Response(serializer.data, status=HTTP_201_CREATED)

    @favorite.mapping.delete
    def delete_favorite(self, *args, **kwargs):
        recipe = get_object_or_404(Recipe, pk=kwargs['pk'])
        user = self.request.user
        recipe.fav_recipe.filter(user=user).delete()
        return Response(status=HTTP_204_NO_CONTENT)

# TODO Посмотреть про Inline, сделать общий метод, mapping, файлы в тг
