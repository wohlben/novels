from django.forms import ModelForm
from novels.models import Fiction

class WatchingForm(ModelForm):
    class Meta:
        model = Fiction
        fields = ['id']
