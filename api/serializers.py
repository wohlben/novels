from rest_framework.serializers import ModelSerializer as _ModelSerializer
from novels.models import Chapter as _Chapter, Fiction as _Fiction
from profiles.models import ReadingProgress as _ReadingProgress


class ChapterSerializer(_ModelSerializer):
    class Meta:
        model = _Chapter
        fields = ("id", "published", "title", "content")


class FictionListSerializer(_ModelSerializer):
    class Meta:
        model = _Fiction
        fields = ("id", "title", "author")


class ChapterListSerializer(_ModelSerializer):
    fiction = FictionListSerializer()

    class Meta:
        model = _Chapter
        fields = ("id", "title", "published", "fiction", "discovered")


class FictionSerializer(_ModelSerializer):
    chapters = ChapterListSerializer(many=True, source="chapter_set")

    class Meta:
        model = _Fiction
        depth = 1
        fields = ("title", "author", "chapters")


class ReadingProgressSerializer(_ModelSerializer):
    class Meta:
        model = _ReadingProgress
        fields = ("id", "progress", "chapter", "timestamp")
