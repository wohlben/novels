from rest_framework.fields import CharField, IntegerField
from rest_framework.serializers import ModelSerializer as _ModelSerializer, ListField
from novels.models import Chapter as _Chapter, Fiction as _Fiction, Author as _Author
from profiles.models import ReadingProgress as _ReadingProgress
from scrapes.models import Parser as _Parser


class AuthorSerializer(_ModelSerializer):
    class Meta:
        model = _Author
        fields = ("id", "name", "url", "fictions")

    class SimpleFictionSerializer(_ModelSerializer):
        class Meta:
            model = _Fiction
            depth = 1
            fields = ("id", "title", "author", "chapters")

        class SimpleChapterSerializer(_ModelSerializer):
            class Meta:
                model = _Chapter
                fields = ("id", "title", "published")

        chapters = SimpleChapterSerializer(many=True, source="chapter_set")

    fictions = SimpleFictionSerializer(many=True, source="fiction_set")


class ChapterListSerializer(_ModelSerializer):
    class Meta:
        model = _Chapter
        fields = ("id", "title", "published", "fiction", "discovered")

    class SimpleFictionSerializer(_ModelSerializer):
        class SimpleAuthorSerializer(_ModelSerializer):
            class Meta:
                model = _Author
                fields = ("id", "name")

        author = SimpleAuthorSerializer()

        class Meta:
            model = _Fiction
            fields = ("id", "title", "author", "chapters")

    fiction = SimpleFictionSerializer()


class ChapterSerializer(_ModelSerializer):
    class Meta:
        model = _Chapter
        fields = ("id", "published", "title", "content", "fiction", "reading_progress")

    class SimpleFictionSerializer(_ModelSerializer):
        class Meta:
            model = _Fiction
            fields = ("id", "title", "author", "chapters")

        class SimpleAuthorSerializer(_ModelSerializer):
            class Meta:
                model = _Author
                fields = ("id", "name")

        class SimpleChapterSerializer(_ModelSerializer):
            reading_progress = IntegerField(source="progress")

            class Meta:
                model = _Chapter
                fields = ("id", "title", "published", "reading_progress")

        author = SimpleAuthorSerializer()
        chapters = SimpleChapterSerializer(many=True, source="chapter_set")

    reading_progress = IntegerField(source="progress")
    fiction = SimpleFictionSerializer()


class FictionSerializer(_ModelSerializer):
    class Meta:
        model = _Fiction
        fields = ("id", "title", "author", "chapters")

    class SimpleAuthorSerializer(_ModelSerializer):
        class Meta:
            model = _Author
            fields = ("id", "name")

    class SimpleChapterSerializer(_ModelSerializer):
        reading_progress = IntegerField(source="progress")

        class Meta:
            model = _Chapter
            fields = ("id", "title", "published", "reading_progress")

    author = SimpleAuthorSerializer()
    chapters = SimpleChapterSerializer(many=True, source="chapter_set")


class FictionListSerializer(_ModelSerializer):
    class Meta:
        model = _Fiction
        fields = ("id", "title", "author")

    class SimpleAuthorSerializer(_ModelSerializer):
        class Meta:
            model = _Fiction
            fields = ("id", "name")

    author = SimpleAuthorSerializer()


class UpdatedSerializer(_ModelSerializer):
    class Meta:
        model = _Chapter
        fields = (
            "id",
            "title",
            "published",
            "external_url",
            "discovered",
            "internal_url",
            "fiction",
            "reading_progress",
        )

    class SimpleFictionSerializer(_ModelSerializer):
        class Meta:
            model = _Fiction
            fields = ("title", "author", "id", "internal_url")

        class SimpleAuthorSerializer(_ModelSerializer):
            class Meta:
                model = _Author
                fields = ("id", "name")

        internal_url = CharField(source="get_absolute_url")
        author = SimpleAuthorSerializer()

    reading_progress = IntegerField(source="progress")
    internal_url = CharField(source="get_absolute_url")
    external_url = CharField(source="url")
    fiction = SimpleFictionSerializer(many=False)


class ReadingProgressSerializer(_ModelSerializer):
    class Meta:
        model = _ReadingProgress
        fields = ("progress", "chapter", "timestamp")


class ParserSerializer(_ModelSerializer):
    class Meta:
        model = _Parser
        fields = ("id",)
