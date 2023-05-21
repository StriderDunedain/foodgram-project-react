from django.core import validators
from django.db import models


class HexColorField(models.CharField):

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('max_length', 7)
        super().__init__(*args, **kwargs)
        self.validators.append(
            validators.RegexValidator(
                regex=r'#([a-fA-F0-9]{6})',
                message=('Введите корректное значение HEX кода цвета'),
            )
        )
