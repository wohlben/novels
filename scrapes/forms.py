from django import forms
from novels.models import Fiction, Chapter


class RequeueChapterForm(forms.ModelForm):
    requeue = forms.BooleanField()
    class Meta:
        model = Chapter
        fields = []

class RequeueNovelForm(forms.ModelForm):
    requeue = forms.BooleanField()
    class Meta:
        model = Fiction
        fields = []
