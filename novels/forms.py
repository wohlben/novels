from django.forms import ModelForm, BooleanField
from novels.models import Fiction


class WatchingForm(ModelForm):
    watch = BooleanField
    class Meta:
        model = Fiction
        fields = []
