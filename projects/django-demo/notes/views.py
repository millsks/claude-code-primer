from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets

from .models import Note
from .serializers import NoteSerializer


class NoteViewSet(viewsets.ModelViewSet):
    queryset = Note.objects.all()
    serializer_class = NoteSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["pinned"]
    search_fields = ["title", "body"]
    ordering_fields = ["created_at", "updated_at", "title"]
