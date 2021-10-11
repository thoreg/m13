from rest_framework import permissions, viewsets

from zalando.models import FeedRow

from .serializers import FeedRowSerializer


class FeedRowViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows to interact with custom feed (rows)
    """
    queryset = FeedRow.objects.all()
    serializer_class = FeedRowSerializer
    permission_classes = [permissions.IsAuthenticated]
