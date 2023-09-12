from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework.decorators import action
from rest_framework.mixins import Response
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.status import HTTP_201_CREATED, HTTP_204_NO_CONTENT
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from core.utils import shopping_cart_util
from recipes.models import Cart, Favorite, Ingredient, Recipe, Tag
from users.models import Subscription, User
from .filters import IngredientFilter, RecipeFilter
from .pagination import RecipeUserPagination
from .serializers import (
    IngredientSerializer, RecipeCreateSerializer,
    RecipeDetailSerializer, RecipeSerializer,
    SubscriptionSerializer, TagSerializer, UserSerializer
)


class UserViewSet(DjoserUserViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = RecipeUserPagination

    @action(
        detail=False,
        methods=['GET'],
        permission_classes=(IsAuthenticated,)
    )
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

    @action(
        detail=True,
        methods=['POST'],
        permission_classes=(IsAuthenticated,)
    )
    def subscribe(self, *args, **kwargs):
        author = get_object_or_404(User, pk=kwargs['id'])
        user = self.request.user
        try:
            Subscription.objects.create(author=author, subscriber=user)
            serializer = SubscriptionSerializer(author)
            return Response(serializer.data, status=HTTP_201_CREATED)
        except IntegrityError as e:
            return Response(
                data={'exists': e},
                status=HTTP_204_NO_CONTENT
            )

    @subscribe.mapping.delete
    def delete_subscribe(self, *args, **kwargs):
        author = get_object_or_404(User, pk=kwargs['id'])
        user = self.request.user
        author.subscriptions.filter(subscriber=user).delete()
        return Response(status=HTTP_204_NO_CONTENT)


class TagViewSet(ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)


class IngredientViewSet(ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)

    filter_backends = (IngredientFilter,)
    search_fields = ('^name',)


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    pagination_class = RecipeUserPagination
    permission_classes = (IsAuthenticatedOrReadOnly,)

    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return super().get_serializer_class()
        return RecipeCreateSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def common_post_method(self, model, recipe_id):
        recipe = get_object_or_404(Recipe, pk=recipe_id)
        user = self.request.user
        model.objects.create(user=user, recipe=recipe)
        serializer = RecipeDetailSerializer(recipe)
        return Response(serializer.data, status=HTTP_201_CREATED)

    @action(
        detail=False,
        methods=['GET'],
        permission_classes=(IsAuthenticated,)
    )
    def download_shopping_cart(self, request):
        return shopping_cart_util(user=request.user)

    @action(
        detail=True,
        methods=['POST'],
        permission_classes=(IsAuthenticated,)
    )
    def shopping_cart(self, request, pk):
        return self.common_post_method(model=Cart, recipe_id=pk)

    @shopping_cart.mapping.delete
    def delete_shopping_cart(self, *args, **kwargs):
        recipe = get_object_or_404(Recipe, pk=kwargs['pk'])
        recipe.cart_recipe.filter(user=self.request.user).delete()
        return Response(status=HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=['POST'],
        permission_classes=(IsAuthenticated,)
    )
    def favorite(self, request, pk):
        return self.common_post_method(model=Favorite, recipe_id=pk)

    @favorite.mapping.delete
    def delete_favorite(self, *args, **kwargs):
        recipe = get_object_or_404(Recipe, pk=kwargs['pk'])
        recipe.fav_recipe.filter(user=self.request.user).delete()
        return Response(status=HTTP_204_NO_CONTENT)
