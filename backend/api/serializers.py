from django.core.exceptions import ValidationError
from django.db.models import F
from drf_extra_fields.fields import Base64ImageField
from rest_framework.serializers import (ModelSerializer, SerializerMethodField,
                                        SlugRelatedField)

from recipes.models import Favorite, Ingredient, IngredientAmount, Recipe, Tag
from users.models import CustomUser


class ShortRecipeSerializer(ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
        read_only_fields = ('__all__',)


class UserSerializer(ModelSerializer):

    is_subscribed = SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'password'
        )
        extra_kwargs = {'password': {'write_only': True}}
        read_only_fields = ('is_subscribed',)

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user

        if user.is_anonymous or (user == obj):
            return False

        return user.subscriptions.filter(author=obj).exists()

    def create(self, validated_data):
        user = CustomUser(
            email=validated_data['email'],
            username=validated_data['username'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


class UserSubscribeSerializer(UserSerializer):
    recipes = ShortRecipeSerializer(many=True, read_only=True)
    recipes_count = SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count'
        )
        read_only_fields = ('__all__',)

    def get_is_subscribed(*args):
        return True

    def get_recipes_count(self, user):
        return user.recipes.count()


class TagSerializer(ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')
        read_only = ('__all__',)


class IngredientSerializer(ModelSerializer):
    class Meta:
        model = Ingredient
        fields = '__all__'
        read_only = ('__all__',)


class RecipeSerializer(ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    author = UserSerializer(read_only=True)
    ingredients = SerializerMethodField()
    is_favorited = SerializerMethodField()
    is_in_shopping_cart = SerializerMethodField()
    name = SerializerMethodField()
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

    def get_ingredients(self, recipe):
        ingredients = recipe.ingredients.values(
            'id', 'name', 'measurement_unit', amount=F('recipe__amount')
        )
        return ingredients

    def get_is_favorited(self, recipe):
        user = self.context.get('view').request.user

        if not user.is_anonymous:
            return user.favorites.filter(recipe=recipe).exists()

        return False

    def get_is_in_shopping_cart(self, recipe):
        user = self.context.get('view').request.user

        if not user.is_anonymous:
            return user.carts.filter(recipe=recipe).exists()

        return False

    def validate(self, data):
        tags_ids = self.initial_data.get('tags')
        ingredients = self.initial_data.get('ingredients')

        if not tags_ids or not ingredients:
            raise ValidationError('Недостаточно данных')

        tags = Tag.objects.filter(id__in=tags_ids)
        data.update(
            {
                'tags': tags,
                'ingredients': ingredients,
                'author': self.context.get('request').user,
            }
        )
        return data

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        objs = [
            IngredientAmount(
                recipe=recipe, ingredients=ingredient, amount=amount
            ) for ingredient, amount in ingredients.values()
        ]
        IngredientAmount.objects.bulk_create(objs)

        return recipe

    def update(self, recipe, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')

        for key, value in validated_data.items():
            if hasattr(recipe, key):
                setattr(recipe, key, value)

        if tags:
            recipe.tags.clear()
            recipe.tags.set(tags)

        if ingredients:
            recipe.ingredients.clear()
            objs = [
                IngredientAmount(
                    recipe=recipe, ingredients=ingredient, amount=amount
                ) for ingredient, amount in ingredients.values()
            ]
            IngredientAmount.objects.bulk_create(objs)

        recipe.save()
        return recipe


class FavoriteSerializer(ModelSerializer):
    name = SlugRelatedField(
        source='recipe', slug_field='name', read_only=True)
    image = SerializerMethodField()
    cooking_time = SlugRelatedField(
        source='recipe', slug_field='cooking_time', read_only=True)

    class Meta:
        model = Favorite
        fields = ('id', 'name', 'image', 'cooking_time')

    def get_image(self, obj):
        return self.context.get('request').build_absolute_uri(
            obj.recipe.image.url)


class CartSerializer(RecipeSerializer):
    class Meta(RecipeSerializer.Meta):
        fields = ('id', 'name', 'image', 'cooking_time')
        read_only_fields = ('id', 'name', 'image', 'cooking_time')
