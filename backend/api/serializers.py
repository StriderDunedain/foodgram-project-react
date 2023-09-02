from django.db.transaction import atomic
from drf_extra_fields.fields import Base64ImageField
from djoser.serializers import (
    UserCreateSerializer as DjoserUserCreateSerializer
)
from djoser.serializers import UserSerializer as DjoserUserSerializer
from rest_framework.serializers import (
    CharField, IntegerField, ModelSerializer, SerializerMethodField,
    ValidationError, PrimaryKeyRelatedField
)

from core.constants import OBJECTS_PER_PAGE
from recipes.models import Ingredient, Recipe, RecipeIngredient, Tag
from users.models import User


class UserSerializer(DjoserUserSerializer):
    is_subscribed = SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed'
        )

    def get_is_subscribed(self, user):
        return (user.is_authenticated
                and user.subscriptions.filter(subscriber=user).exists())


class UserCreateSerializer(DjoserUserCreateSerializer):
    class Meta:
        model = User
        fields = (
            'email',
            'username',
            'first_name',
            'last_name',
            'password'
        )


class RecipeDetailSerializer(ModelSerializer):
    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )


class SubscriptionSerializer(ModelSerializer):
    recipes = SerializerMethodField()
    recipes_count = IntegerField(source='recipe_author.count')

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'recipes',
            'recipes_count'
        )

    def get_recipes(self, user):
        recipes_limit = self.context['request'].GET.get(
            'recipes_limit', OBJECTS_PER_PAGE
        )
        recipes = user.recipe_author.all()[:int(recipes_limit)]
        serializer = RecipeDetailSerializer(recipes, many=True)
        return serializer.data


class TagSerializer(ModelSerializer):
    class Meta:
        model = Tag
        fields = (
            'id',
            'name',
            'color',
            'slug'
        )


class IngredientSerializer(ModelSerializer):
    class Meta:
        model = Ingredient
        fields = (
            'id',
            'name',
            'measurement_unit',
        )


class RecipeIngredientSerializer(ModelSerializer):
    id = CharField(source='ingredients.id')
    name = CharField(source='ingredients.name', read_only=True)
    measurement_unit = CharField(
        source='ingredients.measurement_unit',
        read_only=True
    )

    class Meta:
        model = RecipeIngredient
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount'
        )


class RecipeSerializer(ModelSerializer):
    tags = TagSerializer(many=True)
    author = UserSerializer(read_only=True)
    ingredients = RecipeIngredientSerializer(
        many=True,
        source='ingredients_recipe'
    )
    is_favorited = SerializerMethodField(read_only=True)
    is_in_shopping_cart = SerializerMethodField(read_only=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time'
        )

    def get_is_favorited(self, recipe):
        user = self.context['request'].user
        return (user.is_authenticated
                and recipe.fav_recipe.filter(user=user).exists())

    def get_is_in_shopping_cart(self, recipe):
        user = self.context['request'].user
        return (user.is_authenticated
                and recipe.cart_recipe.filter(user=user).exists())


class RecipeCreateSerializer(RecipeSerializer):
    tags = PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        write_only=True,
        many=True
    )

    def validate(self, data):
        ingredients = []

        for ingredient in data['ingredients_recipe']:
            ingredient_id = ingredient.get('ingredients', {}).get('id')
            ingredients.append(ingredient_id)

        if len(set(ingredients)) != len(ingredients):
            raise ValidationError('Ингредиенты повторяются')

        if not data.get('tags', []):
            raise ValidationError('Нет тегов')
        if not data.get('ingredients_recipe', []):
            raise ValidationError('Нет ингредиентов')

        if data.get('cooking_time') <= 0:
            raise ValidationError('Время готовки меньше / равно 0')

        for ingredient in data['ingredients_recipe']:
            if ingredient['amount'] <= 0:
                raise ValidationError(
                    f'Вес ингредиента {ingredient} меньше 0'
                )
        return data

    @atomic()
    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients_recipe')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        for ingredient in ingredients:
            RecipeIngredient.objects.create(
                ingredients_id=ingredient['ingredients']['id'],
                recipe=recipe,
            )
        return recipe

    @atomic()
    def update(self, recipe, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients_recipe')
        super().update(recipe, validated_data)
        recipe.tags.set(tags)
        recipe.ingredients_recipe.all().delete()
        for ingredient in ingredients:
            RecipeIngredient.objects.create(
                ingredients_id=ingredient['ingredients']['id'],
                recipe=recipe,
            )
        return recipe
