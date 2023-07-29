from django.contrib.admin import ModelAdmin, TabularInline, register
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from recipes.forms import TagForm
from recipes.models import (Cart, Favorite, Ingredient, IngredientAmount,
                            Recipe, Tag)
from users.models import Subscription


class IngredientInline(TabularInline):
    model = IngredientAmount
    min_num = 1


@register(IngredientAmount)
class LinksAdmin(ModelAdmin):
    pass


@register(Ingredient)
class IngredientAdmin(ModelAdmin):
    list_display = ('name', 'measurement_unit')
    search_fields = ('name',)
    list_filter = ('name',)

    save_on_top = True


@register(Recipe)
class RecipeAdmin(ModelAdmin):
    list_display = (
        'name',
        'author',
        'get_image',
        'count_favorite',
    )
    search_fields = (
        'name',
        'author__username',
        'tags__name',
    )
    list_filter = ('name', 'author__username', 'tags__name')

    inlines = (IngredientInline,)
    save_on_top = True

    def get_image(self, obj):
        return mark_safe(f'<img src={obj.image.url} width="80" height="30"')

    def count_favorite(self, obj):
        return obj.in_Favorite.count()


@register(Tag)
class TagAdmin(ModelAdmin):
    form = TagForm
    list_display = ('name', 'slug', 'color_code')
    search_fields = ('name', 'color')

    save_on_top = True

    def color_code(self, obj: Tag):
        return format_html(
            '<span style="color: #{};">{}</span>', obj.color[1:], obj.color
        )


@register(Favorite)
class FavoriteAdmin(ModelAdmin):
    list_display = ('user', 'recipe', 'date_added')
    search_fields = ('user__username', 'recipe__name')

    def has_change_permission(self):
        return False

    def has_delete_permission(self):
        return False


@register(Cart)
class CartAdmin(ModelAdmin):
    list_display = ('user', 'recipe', 'date_added')
    search_fields = ('user__username', 'recipe__name')

    def has_change_permission(self):
        return False

    def has_delete_permission(self):
        return False


@register(Subscription)
class SubscriptionAdmin(ModelAdmin):
    list_display = (
        'author__username',
        'subscriber__username',
        'creation_date'
    )
    list_filter = ('author__username', 'author__email')
    search_fields = ('author__username', 'author__email')
