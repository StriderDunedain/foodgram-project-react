from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db.models import (
    CASCADE,
    SET_NULL,
    CharField,
    DateTimeField,
    ForeignKey,
    ImageField,
    ManyToManyField,
    Model,
    PositiveSmallIntegerField,
    TextField,
    UniqueConstraint
)

from core import constants as const

User = get_user_model()


class Tag(Model):
    name = CharField(
        verbose_name='Тэг',
        max_length=const.TAG_NAME_LIMIT,
        unique=True
    )
    color = CharField(
        verbose_name='Hex-цвет тэга',
        max_length=7,
        unique=True,
        db_index=False
    )
    slug = CharField(
        verbose_name='Слаг тэга',
        max_length=const.TAG_SLUG_LIMIT,
        unique=True,
        db_index=False
    )

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'
        ordering = ('name',)

    def __str__(self) -> str:
        return f'{self.name} -> {self.color}'


class Ingredient(Model):
    name = CharField(
        verbose_name='Название ингредиента',
        max_length=55
    )
    measurement_unit = CharField(
        verbose_name='Единицы измерения',
        max_length=25
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('name',)
        constraints = (
            UniqueConstraint(
                fields=('name', 'measurement_unit'),
                name='unique_for_ingredient'
            ),
        )

    def str(self) -> str:
        return f'{self.name}: {self.measurement_unit}'


class Recipe(Model):
    author = ForeignKey(
        verbose_name='Автор рецепта',
        related_name='author',
        to=User,
        on_delete=SET_NULL,
        null=True
    )
    name = CharField(
        verbose_name='Название рецепта',
        max_length=const.RECIPE_NAME_LIMIT
    )
    image = ImageField(
        verbose_name='Изображение рецепта',
        upload_to='recipe_media/'
    )
    description = TextField(
        verbose_name='Описание рецепта',
        max_length=const.RECIPE_DESCRIPTION_LIMIT
    )
    pub_date = DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True,
        editable=False
    )
    ingredients = ManyToManyField(
        verbose_name='Ингредиенты блюда',
        related_name='recipe_ingredients',
        to=Ingredient,
        through='IngredientAmount'
    )
    tags = ManyToManyField(
        verbose_name='Тег',
        related_name='recipe_tags',
        to='Tag'
    )
    cooking_time = PositiveSmallIntegerField(
        verbose_name='Время приготовления',
        default=1,
        validators=(
            MinValueValidator(
                const.MIN_COOKING_TIME,
                'Нельзя так вот делать',
            ),
            MaxValueValidator(
                const.MAX_COOKING_TIME,
                'Долговато ждать придется...',
            )
        )
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-pub_date',)

    def __str__(self) -> str:
        return f'{self.author} -> {self.name}'


class IngredientAmount(Model):
    recipe = ForeignKey(
        verbose_name='Рецепт',
        related_name='recipe',
        to=Recipe,
        on_delete=CASCADE
    )
    ingredients = ForeignKey(
        verbose_name='Ингредиенты',
        related_name='ingredients',
        to=Ingredient,
        on_delete=CASCADE
    )
    amount = PositiveSmallIntegerField(
        verbose_name='Единица измерения',
        default=1,
        validators=(
            MinValueValidator(
                const.MIN_AMOUNT_LIMIT,
                'Маловато выходит...'
            ),
            MaxValueValidator(
                const.MAX_AMOUNT_LIMIT,
                'Что-то многовато...'
            )
        )
    )

    class Meta:
        constraints = (
            UniqueConstraint(
                fields=(
                    'recipe',
                    'ingredients'
                ),
                name='unique_for_ingredientamount'
            ),
        )

    def __str__(self) -> str:
        return f'{self.amount} {self.ingredients}'


class Favorite(Model):
    recipe = ForeignKey(
        verbose_name='Понравившийся рецепт',
        related_name='in_favorites',
        to=Recipe,
        on_delete=CASCADE
    )
    user = ForeignKey(
        verbose_name='Пользователь',
        related_name='favorite_recipes',
        to=User,
        on_delete=CASCADE
    )
    adding_date = DateTimeField(
        verbose_name='Время добавления в избранное',
        auto_now_add=True,
        editable=False
    )

    class Meta:
        constraints = (
            UniqueConstraint(
                fields=(
                    'recipe',
                    'user'
                ),
                name='Рецепт уже в избранных'
            ),
        )

    def __str__(self) -> str:
        return f'{self.user} -> {self.recipe}'


class Favorite(Model):
    recipe = ForeignKey(
        verbose_name='Рецепт в корзине',
        related_name='in_cart',
        to=Recipe,
        on_delete=CASCADE
    )
    user = ForeignKey(
        verbose_name='Пользователь',
        related_name='cart_recipes',
        to=User,
        on_delete=CASCADE
    )
    adding_date = DateTimeField(
        verbose_name='Время добавления в корзину',
        auto_now_add=True,
        editable=False
    )

    class Meta:
        constraints = (
            UniqueConstraint(
                fields=(
                    'recipe',
                    'user'
                ),
                name='Рецепт уже в корзине'
            ),
        )

    def __str__(self) -> str:
        return f'{self.user} -> {self.recipe}'
