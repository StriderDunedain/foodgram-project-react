from django.urls import include, path
from rest_framework import routers

from api.views import (
    IngredientViewSet, RecipeViewSet,
    TagViewSet, UserViewSet
)

router = routers.DefaultRouter()

router.register('users', UserViewSet)
router.register('tags', TagViewSet)
router.register('recipes', RecipeViewSet)
router.register('ingredients', IngredientViewSet)


urlpatterns = [
    path('', include(router.urls)),
]
