from django.contrib.admin import ModelAdmin, register

from .models import Subscription, User


@register(User)
class UserAdmin(ModelAdmin):
    list_display = ('username', 'email', 'first_name')
    search_fields = ('username', 'email')


@register(Subscription)
class SubscriptionAdmin(ModelAdmin):
    list_display = ('author', 'subscriber')
