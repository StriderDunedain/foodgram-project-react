from rest_framework.pagination import PageNumberPagination

from core.constants import OBJECTS_PER_PAGE


class LimitPageNumberPagination(PageNumberPagination):
    page_size = OBJECTS_PER_PAGE
    page_size_query_param = 'limit'
