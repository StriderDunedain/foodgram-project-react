import re

from django.core.exceptions import ValidationError


def validate_usernames(value):
    pattern = r'^[\w.@+-]+\Z'
    exemple = re.match(pattern, value, flags=re.I)
    if exemple is None:
        raise ValidationError('Недопустимый символ в имени пользователя')
