from django.forms import ModelForm, BooleanField, Form, CharField, Textarea
from novels.models import Fiction


class BulkWatchForm(Form):
    url_list = CharField(widget=Textarea)


class WatchingForm(ModelForm):
    watch = BooleanField

    class Meta:
        model = Fiction
        fields = []
