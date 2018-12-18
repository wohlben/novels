from django import forms
from novels.models import Fiction

class WatchingForm(forms.Form):
    novel_id = forms.IntegerField()        
