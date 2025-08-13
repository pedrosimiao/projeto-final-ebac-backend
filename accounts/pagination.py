# accounts/pagination.py

from rest_framework.pagination import CursorPagination

# Paginação para as listas longas de users (page de Follows no frontend)
class UserListCursorPagination(CursorPagination):
    page_size = 20
    page_size_query_param = 'limit'
    cursor_query_param = 'cursor'
    ordering = '-joined_at'

# Paginação para a lista de users sugeridos ("Yout might like" no component RightSidebar)
class SuggestedUsersCursorPagination(CursorPagination):
    page_size = 5
    page_size_query_param = 'limit'
    cursor_query_param = 'cursor'
    # aAlista já é embaralhada randomicamente
    # mas se o backend for paginar o resultado da randomização,
    # um campo estável (como 'id') seria necessário para CursorPagination
    # 'random.shuffle' na @action suggested em user_viewset randomiza a lista completa antes da paginação,
    # deixo o'id' como um fallback seguro, embora o principal seja o shuffle
    ordering = 'id'