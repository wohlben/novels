from django_filters.rest_framework import DjangoFilterBackend
from api.serializers import FictionListSerializer, FictionSerializer, ChapterListSerializer, ChapterSerializer
from novels.models import Fiction, Chapter
from rest_framework import viewsets

class FictionViewSet(viewsets.ModelViewSet):
    queryset = Fiction.objects.all().order_by('title')
    filter_backends = (DjangoFilterBackend,)
    filter_fields = ('monitored', 'author')

    def get_serializer_class(self):
        if self.action == 'list':
            return FictionListSerializer
        else:
            return FictionSerializer


class ChapterViewSet(viewsets.ModelViewSet):
    #queryset = Chapter.objects.filter(fiction__monitored=True).order_by('published')
    queryset = Chapter.objects.all().order_by('-id')
    filter_backends = (DjangoFilterBackend,)
    filter_fields = ('fiction', 'fiction__monitored')

    def get_serializer_class(self):
        if self.action == 'list':
            return ChapterListSerializer
        else:
            return ChapterSerializer
