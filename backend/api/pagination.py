from rest_framework.pagination import PageNumberPagination

from core.constants import OBJECTS_PER_PAGE


class RecipeUserPagination(PageNumberPagination):
    page_size = OBJECTS_PER_PAGE
