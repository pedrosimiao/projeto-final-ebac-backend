# config/pagination/cursor_pagination.py

from rest_framework.pagination import CursorPagination

class CustomCursorPagination(CursorPagination):
    # quantidade default de itens por página.
    page_size = 10
    
    # permite alterar o tamanho da página via o parâmetro de query '?limit=X'.
    page_size_query_param = 'limit'
    
    # nome do parâmetro de query para o cursor (ex: '?cursor=some_value').
    cursor_query_param = 'cursor'
    
    # ordenação exige indexação nos modelos Post e Comment.
    # ordering = '-created_at'
    
    # limite máximo para o page_size que o cliente pode solicitar.
    # max_page_size = 50