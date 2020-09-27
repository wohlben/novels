from datetime import datetime

from rest_framework.fields import CharField, IntegerField, ModelField, BooleanField, Field, TimeField, DateTimeField
from rest_framework.relations import HyperlinkedRelatedField, PrimaryKeyRelatedField
from rest_framework.serializers import ModelSerializer as _ModelSerializer, ListField
from novels.models import Chapter as _Chapter, Fiction as _Fiction, Author as _Author
from profiles.models import ReadingProgress as _ReadingProgress
from scrapes.models import Parser as _Parser


class TimestampField(DateTimeField):
    def to_representation(self, value):
        if value:
            return int(value.timestamp() * 1000)
        return 0


class StringifyPrimaryRelated(PrimaryKeyRelatedField):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def to_representation(self, value):
        value = super().to_representation(value)
        if value:
            return str(value)
        return value


class AuthorSerializer(_ModelSerializer):
    class Meta:
        model = _Author
        fields = ("id", "name")

    id = CharField()


class AuthorDetailSerializer(_ModelSerializer):
    class Meta:
        model = _Author
        fields = ("id", "name", "fictions")

    fictions = StringifyPrimaryRelated(many=True, source="fiction_set", read_only=True)
    id = CharField()


class ChapterListSerializer(_ModelSerializer):
    class Meta:
        model = _Chapter
        fields = ("id", "fictionId", "title", "published", "discovered", "progress")

    id = CharField()
    fictionId = CharField(source="fiction.id")
    # authorId = CharField(source="fiction.author.id", default=None, required=False)
    progress = IntegerField(default=0, required=False)
    discovered = TimestampField()
    published = TimestampField()


class ChapterSerializer(ChapterListSerializer):
    class Meta:
        model = _Chapter
        fields = ("id", "fictionId", "title", "published", "discovered", "progress", "content")


class FictionListSerializer(_ModelSerializer):
    class Meta:
        model = _Fiction
        fields = (
            "id",
            "title",
            "authorId",
            "watched",
        )

    id = CharField()
    authorId = CharField(source="author_id", default=None)
    watched = BooleanField()


class FictionSerializer(FictionListSerializer):
    class Meta:
        model = _Fiction
        fields = ("id", "title", "authorId", "watched", "chapters")

    chapters = StringifyPrimaryRelated(many=True, source="chapter_set", read_only=True)


class UpdatedSerializer(_ModelSerializer):
    class Meta:
        model = _Chapter
        fields = ("id", "title", "published", "externalUrl", "discovered", "internalUrl", "fictionId", "progress")

    id = CharField()
    fictionId = CharField(source="fiction_id")
    progress = IntegerField(default=0)
    internalUrl = CharField(source="get_absolute_url")
    externalUrl = CharField(source="url")
    discovered = TimestampField()
    published = TimestampField()


class ReadingProgressSerializer(_ModelSerializer):
    class Meta:
        model = _ReadingProgress
        fields = ("progress", "chapter", "timestamp")


class ParserSerializer(_ModelSerializer):
    class Meta:
        model = _Parser
        fields = ("id",)
