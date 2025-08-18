# posts/serializers/post_serializer.py

from rest_framework import serializers
from ..models import Post
from accounts.serializers import UserBasicSerializer
from storages.backends.s3boto3 import S3Boto3Storage

# *** PostSummarySerializer ***

# serializer para retweet aninhado
# embora haja prevenção no frontend para que retweets não possam ser retwetados
# PostSummarySerializer tem fields limitados para prevenir loop infinito de retweets
class PostSummarySerializer(serializers.ModelSerializer):
    # dados de User relevantes para Post.
    user = UserBasicSerializer(read_only=True)

    # image e video são serializados manualmente para retornar URL completa 
    image = serializers.SerializerMethodField()
    video = serializers.SerializerMethodField()

    class Meta:
        # model de post.py
        model = Post

        # campos relevantes para retweet
        fields = [
            "id",
            "user", # somente dados relevantes do autor do post
            "content",
            "image",
            "video",
            "created_at",
        ]

        read_only_fields = fields

    # Gerenciamento dos campos serializados manualmente
    # SerializerMethodField()
    # self: PostSummarySerializer
    # obj: modelo Post
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


# *** PostSerializer ***

# serializer principal pra um post completo
class PostSerializer(serializers.ModelSerializer):
    # dados de User relevantes para Post.
    user = UserBasicSerializer(read_only=True)

    image = serializers.ImageField(required=False, allow_null=True)
    video = serializers.FileField(required=False, allow_null=True)

    # entrada --> receber a ID do post original
    retweet_id = serializers.PrimaryKeyRelatedField(
        source='retweet',
        queryset=Post.objects.all(),
        allow_null=True,
        required=False,
        write_only=True
    )

    # saída --> exibir os detalhes do post original retweetado
    retweet = PostSummarySerializer(
        read_only=True
    )

    # já vem calculado do banco de dados (função count em post_viewset.py)
    total_comments_count = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Post
        fields = [
            "id",
            "user",
            "content",
            "image",
            "video",
            "retweet_id",
            "retweet",
            "created_at",
            "total_comments_count",
        ]
        read_only_fields = [
            "id",
            "user",
            "retweet",
            "created_at",
            "total_comments_count",
        ]


    # função que retorna a contagem de comments pré-calculada por PostViewSet usando .annotate()
    def get_total_comments_count(self, obj):
        return getattr(obj, 'total_comments_count', 0)

    # sobrescrição da função create pra associar o usuário logado ao post automaticamente
    # validated_data: dicionário de dados já limpos e validados pelo serializer
    def create(self, validated_data):
        try:
            # busca usuário logado e associa ao campo "user"
            validated_data["user"] = self.context["request"].user

            image_file = validated_data.get('image')
            if image_file:
                new_storage = S3Boto3Storage(default_acl='public-read')
                image_file.storage = new_storage
                validated_data['image'] = image_file

            return super().create(validated_data)
        
        except Exception as e:
            print(f"ERROR: Falha ao salvar o post ou arquivo. Erro: {e}")
            raise
