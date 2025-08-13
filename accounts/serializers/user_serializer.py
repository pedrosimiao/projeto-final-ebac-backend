# accounts/serializers/user_serializer.py

from rest_framework import serializers
from accounts.models import User

# Serializer completo para /me e /username
class UserSerializer(serializers.ModelSerializer):

    # profile_picture e cover_image são serializados manualmente para retornar URL completa
    profile_picture = serializers.SerializerMethodField()
    cover_image = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "first_name",
            "last_name",
            "username",
            "email",
            "bio",
            "profile_picture",
            "cover_image",
            "occupation",
            "location",
            "birth_date",
            "joined_at",
        ]
        read_only_fields = ["id", "email", "joined_at"]


    # Gerenciamento dos campos serializados manualmente
    # SerializerMethodField()
    
    # self: instância da classe do serializer (UserSerializer)
    # obj: instância do modelo sendo serializado (User)
    
    # Se obj(User).profile_picture existir,
    # variável request será igual ao "request" (requisição HTTP atual) 
    # do contexto do serializador (contexto passado pela Viewset)
    
    # request.build_absolute_uri(obj.arquivo.url) captura o caminho relativo do arquivo (/media/...) e, 
    # usando as informações do host e do esquema da requisição (HTTP/HTTPS), 
    # constrói a URL completa e acessível publicamente

    # Se a requisição existir, build_absolute_uri monta URL completa a ser retornada
    # pelos campos serializados manualmente (profile_picture e cover_image)
    def get_profile_picture(self, obj):
        if obj.profile_picture:
            # captura o objeto request passado pela viewset para o serializer
            request = self.context.get('request')
            if request is not None:
                return request.build_absolute_uri(obj.profile_picture.url)
        return None

    def get_cover_image(self, obj):
        if obj.cover_image:
            # captura o objeto request passado pela viewset para o serializer
            request = self.context.get('request')
            if request is not None:
                return request.build_absolute_uri(obj.cover_image.url)
        return None


    # to_representation: Transformação de dados do model para o formato do frontend
    # execução após serialização
    # self: instância da classe do serializer (UserSerializer)
    # instance: instância do modelo sendo transformado ou atualizado (User) para a representação de saída
    # data: dicionário de dados brutos a ser enviado em requisição (JSON)
    # data.pop() exclui o valor do dicionário
    def to_representation(self, instance):
        # representação básica do serializer
        data = super().to_representation(instance)
        
        # extrai o valor do campo first_name e o guarda em firstName 
        data["firstName"] = data.pop("first_name")

        # extrai o valor do campo last_name e o guarda em lastName
        data["lastName"] = data.pop("last_name")
        
        return data


    # to_internal_value: Transformação de dados do frontend para o formato do model
    # execução antes da serialização
    # self: instância da classe do serializer (UserSerializer)
    # data: dicionário de dados brutos recebido da requisição (JSON) | IUser
    # data.pop() exclui o valor do dicionário
    def to_internal_value(self, data):
        # copia dos dados que vindos do frontend
        data = data.copy()
        
        if "firstName" in data:
            # extrai o valor do campo firstName e o guarda em first_name
            data["first_name"] = data.pop("firstName")
        
        if "lastName" in data:
            # extrai o valor do campo lastName e o guarda em last_name
            data["last_name"] = data.pop("lastName")
        return super().to_internal_value(data)




# Serializer básico pra aninhamento e menções
class UserBasicSerializer(serializers.ModelSerializer):
    # profile_picture é serializado manualmente para retornar URL completa
    profile_picture = serializers.SerializerMethodField()

    class Meta:
        model = User
        # Campos reduzidos ao essencial
        fields = ['id', 'username', 'first_name', 'last_name', 'profile_picture']
        # Somente leitura
        read_only_fields = ['id', 'username', 'first_name', 'last_name', 'profile_picture']

    # Gerenciamento do campo serializado manualmente
    # self: instância da classe do serializer (UserBasicSerializer)
    # obj: instância do modelo sendo serializado (User)
    def get_profile_picture(self, obj):
        if obj.profile_picture:
            # extrai requisição HTTP
            request = self.context.get('request')
            if request is not None:
                # build_absolute_uri monta URL completa a ser retornada pelo campo profile_picture
                return request.build_absolute_uri(obj.profile_picture.url)
        return None


    # to_representation: Transformação de dados do model para o formato do frontent
    # Executada após serialização
    # self: instância da classe do serializer (UserBasicSerializer)
    # instance: instância do modelo sendo transformado ou atualizado (User) para a representação de saída
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["firstName"] = data.pop("first_name")
        data["lastName"] = data.pop("last_name")
        return data
