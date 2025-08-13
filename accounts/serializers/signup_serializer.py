# accounts/serializers/signup_serializer.py

from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

User = get_user_model()

class SignUpSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password]
    )
    confirm_password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "username",
            "email",
            "password",
            "confirm_password",
        ]

    def to_internal_value(self, data):
        # 1. Cria uma CÓPIA dos dados de entrada.
        # É crucial fazer uma cópia (`data.copy()`) porque o 'data' original que o DRF passa
        # pode ser um QueryDict imutável, e tentar modificá-lo diretamente pode causar erros.
        # Além disso, queremos manipular esta cópia antes de passá-la para o método pai.
        input_data = data.copy() 

        # 2. SEUS MAPEAMENTOS/TRADUÇÕES DE NOMES AQUI (CamelCase para Snake_Case).
        # Esta é a parte central da sua lógica personalizada.
        # Você está pegando os nomes de campo que vêm do frontend ('firstName', 'lastName', 'confirmPassword')
        # e *renomeando-os* para os nomes que o seu modelo Django e o seu serializer esperam ('first_name', 'last_name', 'confirm_password').
        # O `.pop()` remove a chave antiga e retorna o valor, que é então atribuído à nova chave.
        if 'firstName' in input_data:
            input_data['first_name'] = input_data.pop('firstName')
        
        if 'lastName' in input_data:
            input_data['last_name'] = input_data.pop('lastName')
        
        if 'confirmPassword' in input_data:
            input_data['confirm_password'] = input_data.pop('confirmPassword')
        
        # 3. CHAMA O MÉTODO to_internal_value DA CLASSE PAI (`ModelSerializer`).
        # `super().to_internal_value(input_data)` significa:
        # "Agora que eu (seu `SignUpSerializer`) fiz minha parte de tradução dos nomes dos campos,
        # passe esses dados JÁ TRADUZIDOS (`input_data`) para o método `to_internal_value` da classe `ModelSerializer`
        # para que ele faça o restante do trabalho padrão (verificar campos obrigatórios, tipos, etc.)."
        #
        # O valor retornado por `super().to_internal_value` (que chamamos de `internal_value`)
        # é o dicionário final de dados prontos para a validação subsequente (`validate` e `create`).
        internal_value = super().to_internal_value(input_data)
        
        # 4. RETORNA OS DADOS PROCESSADOS.
        # Este é o resultado final do seu método `to_internal_value`.
        return internal_value

    def validate(self, attrs):
        if attrs["password"] != attrs["confirm_password"]:
            raise serializers.ValidationError(
                {"confirm_password": "Passwords do not match."}
            )
        return attrs

    def create(self, validated_data):
        validated_data.pop("confirm_password")
        user = User.objects.create_user(**validated_data)
        return user