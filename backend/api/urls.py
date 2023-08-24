from django.urls import include, path
from rest_framework import routers

from api.views import (IngredientModelViewSet, RecipeModelViewSet,
                       TagModelViewSet, UserModelViewSet)

router = routers.DefaultRouter()

router.register('users', UserModelViewSet)
router.register('tags', TagModelViewSet)
router.register('recipes', RecipeModelViewSet)
router.register('ingredients', IngredientModelViewSet)


urlpatterns = [
    path('', include(router.urls)),
]
