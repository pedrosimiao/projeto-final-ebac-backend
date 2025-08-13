# hashtags/viewsets/hashtag_viewset.py

import random

from rest_framework import viewsets, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response

from ..models import Hashtag
from ..serializers import HashtagSerializer

class HashtagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Hashtag.objects.all()
    serializer_class = HashtagSerializer
    permission_classes = [permissions.IsAuthenticated]

    filter_backends = [filters.SearchFilter]
    search_fields = ['name']

    # lógica para o mock trends card em RightSidebar
    @action(detail=False, methods=['get'])
    def random_trends(self, request):
        """
        lista de hashtags limitada e randomizada
        """
        try:
            limit = int(request.query_params.get('limit', 5))
            if limit <= 0:
                limit = 5
        except ValueError:
            limit = 5

        all_hashtags = self.get_queryset() # all hashtags

        # datasets maiores: talvez otimizar essa randomização no DB-level?
        # para PostgreSQL, usar .order_by('?')
        
        all_ids = list(all_hashtags.values_list('id', flat=True))

        random.shuffle(all_ids)
        selected_ids = all_ids[:limit]

        random_hashtags = all_hashtags.filter(id__in=selected_ids)

        serializer = self.get_serializer(random_hashtags, many=True)
        return Response(serializer.data)
