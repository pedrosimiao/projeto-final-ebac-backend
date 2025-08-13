# comments/serializers/comment_serializer.py

from rest_framework import serializers
from ..models import Comment
from accounts.serializers import UserBasicSerializer
from posts.models import Post

# serializer básico comments aninhados (pai/filho)
class CommentBasicSerializer(serializers.ModelSerializer):
    # dados de User relevantes para comments
    user = UserBasicSerializer(read_only=True)
    reply_count = serializers.SerializerMethodField(read_only=True)

    # image e video são serializados manualmente para retornar URL completa
    image = serializers.SerializerMethodField()
    video = serializers.SerializerMethodField()


    class Meta:
        # model de comment.py
        model = Comment
        fields = [
            "id",
            "user", # somente dados relevantes do autor do comment
            "content",
            "image",
            "video",
            "created_at",
            "reply_count",
        ]
        read_only_fields = fields

    # Gerenciamento dos campos serializados manualmente
    # SerializerMethodField()
    # self: CommentBasicSerializer
    # obj: modelo Comment
    
    # Se obj.image | obj.video existir,
    # variável request será igual ao "request" (requisição HTTP atual) 
    # do contexto do serializador (contexto passado pela Viewset)
    # Se a requisição existir, build_absolute_uri monta URL completa a ser retornada
    # pelos campos serializados manualmente (image e video)
    def get_image(self, obj):
        if obj.image:
            request = self.context.get('request')
            if request is not None:
                return request.build_absolute_uri(obj.image.url)
        return None

    def get_video(self, obj):
        if obj.video:
            request = self.context.get('request')
            if request is not None:
                return request.build_absolute_uri(obj.video.url)
        return None
    
    #  REPLY COUNT
    # função pra obter número de replies de um comment
    # já vem calculado do banco de dados graças a .annotate(reply_count=Count('comments')) 
    # criando o field reply_count para cada comment na queryset em comment_viewset.py
    def get_reply_count(self, obj):
        return getattr(obj, 'reply_count', 0)



# serializer lista de comments "filhos"
# intermediário que chama o serializer certo pra cada filho
class RecursiveCommentSerializer(serializers.Serializer):
    # a função é chamada pra cada comentário filho na lista
    def to_representation(self, value):
        # apendas fields relevantes para os replies aninhados 
        serializer = CommentBasicSerializer(value, context=self.context)
        return serializer.data



# serializer principal pra um comment completo
class CommentSerializer(serializers.ModelSerializer):
    # apendas dados de User relevantes para comments
    user = UserBasicSerializer(read_only=True)

    # post como PrimaryKeyRelatedField para escrita
    # espera o id do Post no payload como post
    # queryset=Post.objects.all() --> DRF validação do ID recebido
    post = serializers.PrimaryKeyRelatedField(queryset=Post.objects.all(), write_only=True)

    # post_id aparecendo na SAÍDA (GET),
    # campo read-only separado
    post_id = serializers.CharField(source='post.id', read_only=True)

    parent_comment = serializers.PrimaryKeyRelatedField(
        queryset=Comment.objects.all(),
        allow_null=True,
        required=False
    )

    # comments representa as respostas diretas ao comment vigente
    # RecursiveCommentSerializer usa apenas os dados relevantes pra serializar a lista
    comments = RecursiveCommentSerializer(many=True, read_only=True)

    image = serializers.ImageField(required=False, allow_null=True)
    video = serializers.FileField(required=False, allow_null=True)
    
    # contagem otimizada de replies
    reply_count = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Comment
        fields = [
            "id",
            "user",
            "post",
            "post_id",
            "parent_comment",
            "content",
            "image",
            "video",
            "created_at",
            "comments",
            "reply_count",
        ]
        read_only_fields = [
            "id",
            "user",
            "post_id",
            "parent_comment",
            "created_at",
            "comments",
            "reply_count",
        ]

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        
        if instance.parent_comment:
            parent_comment_serializer = CommentBasicSerializer(
                instance.parent_comment,
                context=self.context
            )
            representation['parent_comment'] = parent_comment_serializer.data
        else:
            representation['parent_comment'] = None
        
        return representation


    #  REPLY COUNT
    # função pra obter número de replies de um comment
    # se o objeto não foi anotado com Count (na criação), retorna 0.
    def get_reply_count(self, obj):
        return getattr(obj, 'reply_count', 0)
