# comments/viewsets/comment_viewset.py

from rest_framework.viewsets import ModelViewSet


# action decorator: criação de endpoints personalizados (fora do CRUD padrão)
# /users/me/, /posts/count/, etc.
from rest_framework.decorators import action 

# response: respostas HTTP
from rest_framework.response import Response

# status: retorno código de status HTTP
from rest_framework import status

# Count: função de agregação do Django, contagem de valores direto no db
# usando na queryset com .annotate() para adicionar um field calculado ("comments")
from django.db.models import Count

from ..models import Comment
from ..serializers import CommentSerializer
from ..pagination import CommentCursorPagination

from rest_framework.permissions import IsAuthenticated

from storages.backends.s3boto3 import S3Boto3Storage

# ModelViewsSet: 
# operações básicas para gerenciamento de model já embutidas (CRUD)
# (list, retrieve, create, update, destroy)
# criação automática de rotas
class CommentViewSet(ModelViewSet):
    # consulta principal ao db
    # select_related(): carrega dados relacionados na mesma consulta (via JOIN no SQL)
    # prefetch_related: pré-carrega vários dados relacionados a cada objeto principal
    queryset = (
        Comment.objects.all()
        # select_related traz:
        # -usuário do comentário, 
        # -post que ele pertence,
        # -comentário pai (se houver) 
        # -usuário do comentário pai
        .select_related("user", "post", "parent_comment", "parent_comment__user")
        
        # prefetch_related: prefetch para comments filhos e seus usuários
        .prefetch_related("comments", "comments__user")
        
        # Count calcula reply_count no nível do db
        .annotate(reply_count=Count('comments'))
        
        .order_by('-created_at')
    )

    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = CommentCursorPagination

    # função define quais comments a serem buscados
    def get_queryset(self):
        # consulta queryset já otimizado no viewset
        base_queryset = super().get_queryset()

        #  busca ID do post cujo comment é reply 
        # post_id = self.request.query_params.get("post_id")
        
        # post_id via self.kwargs
        post_id = self.kwargs.get("post_id")
        
        #  busca ID do comment cujo comment vigente é reply (comment pai)
        parent_comment_id = self.request.query_params.get("parent_comment_id")

        if self.action == "list":
            if not post_id:
                # Se post_id não for fornecido na listagem, retorna vazio
                return base_queryset.none()

            # filtra os comments pelo ID do post (post_id é compartilhado por todos os níveis de comments)
            # mostrar somente comments que são repliesdo comment vigente
            queryset = base_queryset.filter(post_id=post_id)

            if parent_comment_id:
                # filtra por comments que são replies a um comment específico
                queryset = queryset.filter(parent_comment_id=parent_comment_id)
            else:
                # filtra por comments de nível superior (replies diretos a um post)
                # mostrar somente comments principais
                queryset = queryset.filter(parent_comment__isnull=True)

            return queryset

        return base_queryset

    # função chamada automaticamente antes de salvar um novo comment
    # user: autor do comment => usuário autenticado
    def perform_create(self, serializer):
        # dados validados do serializador
        validated_data = serializer.validated_data

        # processamento da imagem vídeo antes do save
        image_file = validated_data.get('image')
        if image_file:
            image_file.storage = S3Boto3Storage(default_acl='public-read')
            
        video_file = validated_data.get('video')
        if video_file:
            video_file.storage = S3Boto3Storage(default_acl='public-read')

        serializer.save(user=self.request.user)
        serializer.instance = self.get_queryset().get(pk=serializer.instance.pk)

    # DELETE COMMENT
    # sobrescrição da função destroy (ver um comment específico)
    # self: CommentViewSet
    # request: requisição HTTP atual, objeto Request do DRF
    def destroy(self, request, *args, **kwargs):
        comment = self.get_object()
        if comment.user != request.user:
            return Response(
                {"detail": "No permission to delete this comment."},
                status=status.HTTP_403_FORBIDDEN,
            )
        return super().destroy(request, *args, **kwargs)


    # sobrescrição da função retrieve (ver um comment específico)
    # self: CommentViewSet
    # request: requisição HTTP atual, objeto Request do DRF
    # context={"request": request} CommentSerializer obtém acesso ao objeto da requisição
    # alteração da lógica do endpoint pré-existente
    # GET /comments/{id}/
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, context={"request": request})
        return Response(serializer.data)


    # sobrescrição da função list (listagem de comments)
    # self: CommentViewSet
    # request: requisição HTTP atual, objeto Request do DRF
    # context={"request": request} CommentSerializer obtém acesso ao objeto da requisição
    # alteração da lógica do endpoint pré-existente
    # GET /comments/
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True, context={"request": request})
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True, context={"request": request})
        return Response(serializer.data)