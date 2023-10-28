from rest_framework.pagination import PageNumberPagination as Pagination

from constants import PAGINATION_PAGE_SIZE


class PageNumberPagination(Pagination):
    page_size = PAGINATION_PAGE_SIZE
    page_size_query_param = 'limit'
