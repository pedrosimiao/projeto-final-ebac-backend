# posts/viewsets/post_viewset.py

from rest_framework import viewsets

# action decorator: criação de endpoints personalizados (fora do CRUD padrão)
# /users/me/, /posts/count/, etc.
from rest_framework.decorators import action

# response: respostas HTTP
from rest_framework.response import Response

# status: retorno código de status HTTP
from rest_framework import status

from rest_framework.permissions import IsAuthenticated

# Count: função de agregação do Django, contagem de valores direto no db
# usando na queryset com .annotate() para adicionar um field calculado ("comments") 
from django.db.models import Count

from ..models import Post
from ..serializers import PostSerializer
from ..pagination import PostCursorPagination

# (list, retrieve, create, update, destroy)
# criação automática de rotas
class PostViewSet(viewsets.ModelViewSet):
    # consulta principal ao db
    # select_related(): carrega dados relacionados na mesma consulta (via JOIN no SQL)
    # puxa os dados do user autor do post e do usuário do post retuitado (se for o caso) em uma só consulta ao db
    # annotate(): cria o campo total_comments_count e 
    # usa Count para contagem de instâncias do campo "comments" de cada Post
    queryset = Post.objects.all().select_related("user", "retweet__user").annotate\
    (total_comments_count=Count('comments')).order_by('-created_at')

    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = PostCursorPagination

    # lógica de consulta (if user_id) 
    def get_queryset(self):
        # queryset padrão da classe 
        queryset = super().get_queryset()

        # get param user_id na query string da URL
        # /api/posts/?user_id=007 --> user_id = 007
        # /api/posts/ --> user_id = None
        user_id = self.request.query_params.get('user_id', None)

        # user_id? : filter posts where field user id (user__id) === user_id
        if user_id:
            queryset = queryset.filter(user__id=user_id)

        return queryset


    # DELETE POST
    # self: PostViewSet
    # request: requisição HTTP atual, objeto Request do DRF
    def destroy(self, request, *args, **kwargs):
        post = self.get_object()
        if post.user != request.user:
            return Response(
                {"detail": "No permission to delete this post"},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().destroy(request, *args, **kwargs)

    # COUNT POSTS de user específico
    # self: PostViewSet
    # request: requisição HTTP atual, objeto Request do DRF
    # novo endpoint customizado /posts/count/
    @action(detail=False, methods=["get"])
    def count(self, request):
        user_id = request.query_params.get("user_id")
        if not user_id:
            return Response({"detail": "Missing user_id parameter."}, status=status.HTTP_400_BAD_REQUEST)

        count = Post.objects.filter(user_id=user_id).count()
        return Response({"count": count})

    # função chamada automaticamente antes de salvar um novo post
    # user: autor do post => usuário autenticado
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


    # sobrescrição da função retrieve (ver um post específico)
    # self: PostViewSet
    # request: requisição HTTP atual, objeto Request do DRF
    # context={"request": request} PostSerializer obtém acesso ao objeto da requisição
    # alteração da lógica do endpoint pré-existente
    # GET /posts/{id}/
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, context={"request": request})
        return Response(serializer.data)

    # sobrescrição da função list (listagem de posts)
    # self: PostViewSet
    # request: requisição HTTP atual, objeto Request do DRF
    # context={"request": request} PostSerializer obtém acesso ao objeto da requisição
    # alteração da lógica do endpoint pré-existente
    # GET /posts/
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        # paginate_queryset: Retorna uma única page ode results, ou None se pagination estivel disabilitada
        page = self.paginate_queryset(queryset)
        if page is not None:
            # serializa a página atual e responde
            serializer = self.get_serializer(page, many=True, context={"request": request})
            return self.get_paginated_response(serializer.data)
        
        # caso page is None: serializa tudo e responde
        serializer = self.get_serializer(queryset, many=True, context={"request": request})
        return Response(serializer.data)
    


    # GET POSTS de usuários que o usuário logado segue (feed "Following" no frontend)
    # self: PostViewSet
    # request: requisição HTTP atual, objeto Request do DRF
    # novo endpoint customizado /posts/following/
    @action(detail=False, methods=["get"], url_path='following')
    def following_posts(self, request):
        user = self.request.user

        if not user.is_authenticated:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        # IDs de todos os users que o user logado segue
        # values_list('following__id', flat=True): lista de IDs
        followed_users_ids = user.following_set.values_list('following__id', flat=True)

        # consulta ao db: filtra posts de following users
        # select_related(): dados relacionados
        # annotate(): contagens
        queryset = Post.objects.filter(user__id__in=followed_users_ids)\
            .select_related("user", "retweet__user")\
            .annotate(total_comments_count=Count('comments'))\
            .order_by('-created_at')

        # paginação da queryset
        page = self.paginate_queryset(queryset)
        if page is not None:
            # serializa a página atual e retorna a resposta paginada
            # context={"request": request} para PostSerializer ter acesso ao objeto request
            serializer = self.get_serializer(page, many=True, context={"request": request})
            return self.get_paginated_response(serializer.data)

        # caso a paginação esteja desabilitada, serializa todos os posts da queryset
        serializer = self.get_serializer(queryset, many=True, context={"request": request})
        return Response(serializer.data)