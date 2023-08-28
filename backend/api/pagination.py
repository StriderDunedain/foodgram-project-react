from rest_framework.pagination import PageNumberPagination


class RecipeUserPagination(PageNumberPagination):
    page_size = 6
