from rest_framework.fields import CharField
from rest_framework.serializers import ModelSerializer as _ModelSerializer
from novels.models import Chapter as _Chapter, Fiction as _Fiction, Author as _Author
from profiles.models import ReadingProgress as _ReadingProgress
from scrapes.models import Parser as _Parser


class AuthorSerializer(_ModelSerializer):
    class Meta:
        model = _Author
        fields = ("id", "name", "url")


class ChapterSerializer(_ModelSerializer):
    class Meta:
        model = _Chapter
        fields = ("id", "published", "title", "content")


class FictionListSerializer(_ModelSerializer):
    class Meta:
        model = _Fiction
        fields = ("id", "title", "author")


class FictionTitleAuthor(_ModelSerializer):
    internal_url = CharField(source="get_absolute_url")
    author = AuthorSerializer()

    class Meta:
        model = _Fiction
        fields = ("title", "author", "id", "internal_url")


class UpdatedSerializer(_ModelSerializer):
    internal_url = CharField(source="get_absolute_url")
    external_url = CharField(source="url")
    fiction = FictionTitleAuthor(many=False)

    class Meta:
        model = _Chapter
        fields = (
            "id",
            "title",
            "published",
            "external_url",
            "discovered",
            "total_progress",
            "internal_url",
            "fiction",
        )
        read_only_fields = fields


class ChapterListSerializer(_ModelSerializer):
    fiction = FictionListSerializer()

    class Meta:
        model = _Chapter
        fields = ("id", "title", "published", "fiction", "discovered")


class FictionChapterListSerializer(_ModelSerializer):
    class Meta:
        model = _Chapter
        fields = ("id", "title", "published")


class FictionSerializer(_ModelSerializer):
    chapters = FictionChapterListSerializer(many=True, source="chapter_set")

    class Meta:
        model = _Fiction
        depth = 1
        fields = ("title", "author", "chapters")


class ReadingProgressSerializer(_ModelSerializer):
    class Meta:
        model = _ReadingProgress
        fields = ("id", "progress", "chapter", "timestamp")


class ParserSerializer(_ModelSerializer):
    class Meta:
        model = _Parser
        fields = ("id",)
