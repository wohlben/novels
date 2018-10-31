from rest_framework import serializers
from novels.models import Chapter, Fiction
class ChapterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chapter
        fields = ('id', 'published', 'title', 'content')

class FictionListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Fiction
        fields = ('id', 'title', 'author', )

class ChapterListSerializer(serializers.ModelSerializer):
    fiction = FictionListSerializer()
    class Meta:
        model = Chapter
        fields = ('id', 'title' , 'published', 'fiction', 'discovered')


class FictionSerializer(serializers.ModelSerializer):
    chapters = ChapterListSerializer(many=True, source='chapter_set')

    class Meta:
        model = Fiction
        depth = 1
        fields = ('title', 'author', 'monitored', 'chapters')
    

