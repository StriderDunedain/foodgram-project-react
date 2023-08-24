from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db.models import (CASCADE, CharField, ForeignKey, ImageField,
                              ManyToManyField, Model,
                              PositiveSmallIntegerField, SlugField, TextField,
                              UniqueConstraint)

from core import constants as const

User = get_user_model()


class Tag(Model):
    name = CharField(unique=True, max_length=const.TAG_NAME_LIMIT)
    color = CharField(unique=True, max_length=7)
    slug = SlugField(unique=True)

    class Meta:
        ordering = ('name',)


class Ingredient(Model):
    name = CharField(max_length=50)
    measurement_unit = CharField(max_length=25)

    class Meta:
        ordering = ('name',)


class Recipe(Model):
    name = CharField(max_length=const.RECIPE_NAME_LIMIT, db_index=True)
    author = ForeignKey(
        User,
        related_name='recipe_author',
        on_delete=CASCADE
    )
    text = TextField(max_length=const.RECIPE_DESCRIPTION_LIMIT)
    image = ImageField(upload_to='recipes_images/')
    ingredients = ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        related_name='ingredients_recipes'
    )
    tags = ManyToManyField(
        Tag,
        related_name='recipes_tags'
    )
    cooking_time = PositiveSmallIntegerField(
        validators=(
            MinValueValidator(
                0, 'Что-то маловато выходит...'
            ),
        )
    )

    class Meta:
        ordering = ('name',)


class RecipeIngredient(Model):
    recipe = ForeignKey(
        Recipe,
        related_name='recipe',
        on_delete=CASCADE
    )
    ingredients = ForeignKey(
        Ingredient,
        related_name='ingredients',
        on_delete=CASCADE
    )
    amount = PositiveSmallIntegerField(
        default=1,
        validators=(
            MinValueValidator(
                0, 'Слишком мало...'
            ),
        )
    )

    class Meta:
        constraints = (
            UniqueConstraint(
                fields=(
                    'recipe',
                    'ingredients'
                ),
                name='recipe_ingredients_constraint'
            ),
        )


class Cart(Model):
    user = ForeignKey(
        User,
        related_name='cart_user',
        on_delete=CASCADE
    )
    recipe = ForeignKey(
        Recipe,
        related_name='cart_recipe',
        on_delete=CASCADE
    )

    class Meta:
        constraints = (
            UniqueConstraint(
                fields=(
                    'user',
                    'recipe'
                ),
                name='user_recipe_constraint_cart'
            ),
        )


class Favorite(Model):
    user = ForeignKey(
        User,
        related_name='fav_user',
        on_delete=CASCADE
    )
    recipe = ForeignKey(
        verbose_name='Понравившийся рецепт',
        related_name='fav_recipe',
        to=Recipe,
        on_delete=CASCADE
    )

    class Meta:
        constraints = (
            UniqueConstraint(
                fields=(
                    'user',
                    'recipe'
                ),
                name='user_recipe_constraint_fav'
            ),
        )
