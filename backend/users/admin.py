from django.contrib.admin import register
from django.contrib.auth.admin import UserAdmin

from users.models import CustomUser


@register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = (
        'email',
        'username',
        'first_name',
        'last_name'
    )
    search_fields = ('email', 'username')
    list_filter = (
        'email',
        'username',
        'first_name'
    )
