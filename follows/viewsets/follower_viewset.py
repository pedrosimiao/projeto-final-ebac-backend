# follows/viewsets/follower_viewset.py

import uuid

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination

from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

from accounts.serializers import UserBasicSerializer
from ..models import Follow


User = get_user_model()

class FollowListPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class FollowViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    # função auxiliar da classe
    # "_" em _fn: função privada interna da classe
    def _get_user_instance(self, user_id):
        # get_object_or_404 gerencias caso User.DoesNotExist e ValueError,
        return get_object_or_404(User, id=user_id)


    # FOLLOW
    @action(detail=False, methods=["post"])
    def follow(self, request):
        target_user_id = request.data.get("targetUserId") # Obtém o ID do usuário a ser seguido do corpo da requisição (JSON).

        if not target_user_id: # Validação básica: verifica se o ID foi fornecido.
            return Response({"detail": "O ID do usuário a ser seguido (targetUserId) é obrigatório."}, status=status.HTTP_400_BAD_REQUEST)
        
        # validação do UUID
        try:
            uuid.UUID(str(target_user_id)) # Tenta converter a string do ID em um objeto UUID. Se falhar, é um UUID inválido.
        except ValueError:
            return Response({"detail": "Invalid user ID format."}, status=status.HTTP_400_BAD_REQUEST)

        if str(request.user.id) == str(target_user_id): # Impede que um usuário siga a si mesmo.
            return Response({"detail": "You can't follow yourself."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # reutilização da função auxiliar da classe
            target_user_instance = self._get_user_instance(target_user_id) # Usa a função auxiliar para obter a instância do usuário alvo.
        except Exception: # Captura qualquer exceção (incluindo Http404 de get_object_or_404) e retorna 404.
            return Response({"detail": "Target user could not be found."}, status=status.HTTP_404_NOT_FOUND)

        try:
            follow, created = Follow.objects.get_or_create( # Tenta obter uma relação de Follow existente ou cria uma nova se não existir.
                follower=request.user, # O usuário logado é o seguidor.
                following=target_user_instance, # O usuário alvo é quem está sendo seguido.
            )
            if created: # Se a relação foi criada (o usuário não estava seguindo antes).
                return Response({"followed": True, "message": f"You are now following {target_user_instance.username}."}, status=status.HTTP_201_CREATED) # Retorna 201 Created.
            else: # Se a relação já existia (o usuário já seguia).
                return Response({"followed": False, "message": f"You are following {target_user_instance.username}."}, status=status.HTTP_200_OK) # Retorna 200 OK.
        except Exception as e: # Captura erros inesperados durante a operação de banco de dados.
            print(f"Error trying to follow: {e}") # Imprime o erro no console do servidor para depuração.
            return Response({"detail": "An internal error occured while trying to follow."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR) # Retorna 500 Internal Server Error.

    # UNFOLLOW
    @action(detail=False, methods=["delete"])
    def unfollow(self, request):
        target_user_id = request.data.get("targetUserId") # Obtém o ID do usuário a ser deixado de seguir do corpo da requisição.

        if not target_user_id: # Validação de presença do ID.
            return Response({"detail": "targetUserId is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            uuid.UUID(str(target_user_id)) # Validação de formato UUID.
        except ValueError:
            return Response({"detail": "Invalid user ID format."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            target_user_instance = self._get_user_instance(target_user_id) # Obtém a instância do usuário alvo.
        except Exception:
            return Response({"detail": "Target user could not be found."}, status=status.HTTP_404_NOT_FOUND)

        try:
            deleted_count, _ = Follow.objects.filter( # Tenta deletar a relação de seguimento.
                follower=request.user, # O usuário logado é o seguidor.
                following=target_user_instance, # O usuário alvo é quem está sendo deixado de seguir.
            ).delete() # Retorna a contagem de objetos deletados e um dicionário de modelos deletados.

            if deleted_count > 0: # Se algum registro foi deletado.
                return Response({"unfollowed": True, "message": f"You unfollowed {target_user_instance.username}."}, status=status.HTTP_204_NO_CONTENT) # Retorna 204 No Content (sucesso sem conteúdo de retorno).
            else: # Se nenhum registro foi deletado (usuário não seguia antes).
                return Response({"error": "You were not following this user.", "unfollowed": False,}, status=status.HTTP_400_BAD_REQUEST) # Retorna 400 Bad Request.
        except Exception as e:
            print(f"Error trying to unfollow: {e}")
            return Response({"detail": "An internal error occured while trying to unfollow."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    # ENDPOINTS PERSONALIZADOS
    # REGEX:
    # (?P<group>...): named capturing group
    # ^ = negated charachter class
    # [^/.]+: all chars except '/' & '.'

    # FOLLOWERS COUNT
    @action(detail=False, methods=["get"], url_path="users/(?P<user_id>[^/.]+)/followers/count")
    def followers_count(self, request, user_id=None):
        """
        /api/follows/users/{user_id}/followers/count/
        """
        user_instance = self._get_user_instance(user_id)
        count = Follow.objects.filter(following=user_instance).count()
        return Response({"count": count}, status=status.HTTP_200_OK)


    # FOLLOWING COUNT
    @action(detail=False, methods=["get"], url_path="users/(?P<user_id>[^/.]+)/following/count")
    def following_count(self, request, user_id=None):
        """
        /api/follows/users/{user_id}/following/count/
        """
        user_instance = self._get_user_instance(user_id)
        count = Follow.objects.filter(follower=user_instance).count()
        return Response({"count": count}, status=status.HTTP_200_OK)


    # CURRENT USER FOLLOWING STATUS
    @action(detail=False, methods=["get"], url_path="users/(?P<target_user_id>[^/.]+)/is_followed_by_me")
    def is_followed_by_me(self, request, target_user_id=None):
        """
        /api/follows/users/{target_user_id}/is_followed_by_me/
        """
        if not request.user.is_authenticated:
            return Response({"is_followed_by_me": False}, status=status.HTTP_200_OK)

        target_user_instance = self._get_user_instance(target_user_id)
        is_followed = Follow.objects.filter(follower=request.user, following=target_user_instance).exists()
        return Response({"is_followed_by_me": is_followed}, status=status.HTTP_200_OK)


    # FOLLOWERS LIST (PAGINATED)
    @action(detail=False, methods=["get"], url_path="users/(?P<user_id>[^/.]+)/followers")
    def followers_list(self, request, user_id=None):
        user_instance = self._get_user_instance(user_id)
        
        queryset = Follow.objects.filter(following=user_instance).select_related("follower")
        
        paginator = FollowListPagination()
        page = paginator.paginate_queryset(queryset, request)
        
        if page is not None:
            serializer = UserBasicSerializer([f.follower for f in page], many=True)
            return paginator.get_paginated_response(serializer.data)
        
        serializer = UserBasicSerializer([f.follower for f in queryset], many=True)
        return Response(serializer.data)


    # FOLLOWING LIST (PAGINATED)
    @action(detail=False, methods=["get"], url_path="users/(?P<user_id>[^/.]+)/following")
    def following_list(self, request, user_id=None):
        user_instance = self._get_user_instance(user_id)
        
        queryset = Follow.objects.filter(follower=user_instance).select_related("following")
        
        paginator = FollowListPagination()
        page = paginator.paginate_queryset(queryset, request)
        
        if page is not None:
            serializer = UserBasicSerializer([f.following for f in page], many=True)
            return paginator.get_paginated_response(serializer.data)
        
        serializer = UserBasicSerializer([f.following for f in queryset], many=True)
        return Response(serializer.data)