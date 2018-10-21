from rest_framework import serializers
from novels.models import Chapter, Fiction

class FictionListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Fiction
        fields = ('id', 'title', 'author', )

class FictionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Fiction
        fields = '__all__'

class ChapterListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chapter
        fields = ('id', 'fiction', 'title' , 'published', 'discovered', )

class ChapterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chapter
        fields = '__all__'
