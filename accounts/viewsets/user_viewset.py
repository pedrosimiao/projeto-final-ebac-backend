# accounts/viewsets/user_viewset.py

from rest_framework import viewsets, permissions

# action decorator: criação de endpoints personalizados (fora do CRUD padrão)
# /users/me/, /posts/count/, etc.
from rest_framework.decorators import action 

# response: respostas HTTP
from rest_framework.response import Response

# status: retorno código de status HTTP
from rest_framework import status

# Encapsulate filters as objects that can then be combined logically (using & and |)
# permite buscas avançadas (filtragem via combinação lógica) 
from django.db.models import Q

from ..models import User
from ..serializers import UserSerializer, UserProfileUpdateSerializer, UserBasicSerializer
from follows.models import Follow

# paginadores dedicados
from ..pagination import UserListCursorPagination, SuggestedUsersCursorPagination


# ReadOnlyModelViewSet: limitado a listagem e recuperação de dados do model
class UserViewSet(viewsets.ReadOnlyModelViewSet):
    # consulta principal ao db
    queryset = User.objects.all().order_by('-joined_at')

    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'username' # achar user específico via username

    pagination_class = UserListCursorPagination

    #  CURRENT USER
    # self: UserViewSet
    # request: requisição HTTP atual, objeto Request do DRF 
    # serializa user usando as configurações e dados da requisição HTTP atual
    # novo endpoint customizado /users/me/
    @action(detail=False, methods=["get", "put", "patch"])
    def me(self, request):
        user = request.user  # JWT auth user logado

        # requisição dos dados completos do user logado
        if request.method == "GET":
            # GET --> UserSerializer
            # context={"request": request} UserSerializer obtém acesso ao objeto da requisição
            serializer = UserSerializer(user, context={"request": request})
            return Response(serializer.data)

        # requisição de atualização de dados (passíveis de atualização) do user logado
        elif request.method in ["PUT", "PATCH"]:
            # PUT/PATCH --> UserProfileUpdateSerializer
            # context={"request": request} UserProfileUpdateSerializer obtém acesso ao objeto da requisição
            serializer = UserProfileUpdateSerializer(
                # caso seja PATCH => atualização parcial
                user, data=request.data, partial=(request.method == "PATCH"), context={"request": request}
            )
            # validação
            if serializer.is_valid(raise_exception=True):
                serializer.save() # salva mudanças no db
                return Response(serializer.data) # retorna dados atualizados

        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


    # SEARCH BASIC USER DATA (para Mentions, post cards e comment cards no frontend)
    # self: UserViewSet
    # request: requisição HTTP atual, objeto Request do DRF
    # novo endpoint customizado /users/search/?q=...
    @action(detail=False, methods=['get'])
    def search(self, request):
        # resgada o que for digitado
        query = request.query_params.get('q', '') 

        if not query:
            # retorna lista vazia caso não haja parametro digitado
            return Response([], status=status.HTTP_200_OK)

        # Otimização: use select_related para a queryset
        # filtra os usuários por username, first_name ou last_name (case insensitive)
        # "Q" pra juntar as condições 
        users = self.get_queryset().filter(
            Q(username__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query)
        ) 
        
        users = users[:10] # limite de resultados para busca

        # usa serializer básico pra aninhamento e menções
        serializer = UserBasicSerializer(users, many=True, context={"request": request})
        return Response(serializer.data)


    # SUGGESTED USERS
    # # self: UserViewSet
    # request: requisição HTTP atual, objeto Request do DRF
    # serializa user usando as configurações e dados da requisição HTTP atual
    # novo endpoint customizado /users/suggested/
    @action(detail=False, methods=['get'], pagination_class=SuggestedUsersCursorPagination)
    def suggested(self, request):
        current_user = request.user # JWT auth user logado

        all_users = self.get_queryset().exclude(id=current_user.id).exclude(username='admin')

        # busca quais usuários o user logado já segue
        # following_set => relacionamento do model Follow
        followed_users_ids = current_user.following_set.values_list('following__id', flat=True)
        
        # remove usuários já seguidos da lista de sugestões
        suggested_users_queryset = all_users.exclude(id__in=followed_users_ids)

        # paginação personalizada pras sugestões
        page = self.paginate_queryset(suggested_users_queryset)

        # serializa os usuários sugeridos (paginados) com o UserBasicSerializer
        # context={"request": request} UserBasicSerializer obtém acesso ao objeto da requisição
        if page is not None:
            serializer = UserBasicSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        
        # fallback
        serializer = UserBasicSerializer(suggested_users_queryset, many=True, context={'request': request})
        return Response(serializer.data)


    #  SEARCH USER
    # sobrescrição de retrieve: get_serializer => UserSerializer
    # self: UserViewSet
    # request: requisição HTTP atual, objeto Request do DRF
    # serializa user usando as configurações e dados da requisição HTTP atual
    # GET /users/{username}/
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        
        serializer = self.get_serializer(instance, context={"request": request})
        return Response(serializer.data)


    # LIST USERS (excluir?)
    # sobrescrição de list: get_serializer => UserSerializer
    # self: UserViewSet
    # request: requisição HTTP atual, objeto Request do DRF
    # serializa user usando as configurações e dados da requisição HTTP atual
    # GET /users/
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset) # paginador padrão do ViewSet

        # context={"request": request} UserSerializer obtém acesso ao objeto da requisição
        if page is not None:
            serializer = self.get_serializer(page, many=True, context={"request": request})
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True, context={"request": request})
        return Response(serializer.data)