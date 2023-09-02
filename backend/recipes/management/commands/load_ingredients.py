import json

from django.core.management.base import BaseCommand

from foodgram.settings import BASE_DIR
from recipes.models import Ingredient


class Command(BaseCommand):
    def handle(self, *args, **options):
        ingredient_json_path = BASE_DIR / 'data' / 'ingredients.json'
        ingredients_data = json.loads(ingredient_json_path.read_text())
        print('Загрузка ингредиентов началась...')
        for ingredient in ingredients_data:
            try:
                if not Ingredient.objects.filter(name=ingredient['name']).exists():
                    Ingredient.objects.create(**ingredient)
                else:
                    print(f'Ингредиент {ingredient["name"]} уже есть в базе')
            except Exception as exc:
                print(
                    f'Ингредиент {ingredient["name"]} не был загружен. '
                    f'Ошибка {exc}'
                )
        print('Ингредиенты загружены')
