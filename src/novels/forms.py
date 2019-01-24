from django.forms import (
    ModelForm as _ModelForm,
    BooleanField as _BooleanField,
    Form as _Form,
    CharField as _CharField,
    Textarea as _Textarea,
)
from novels.models import Fiction as _Fiction


class BulkWatchForm(_Form):
    url_list = _CharField(widget=_Textarea)


class WatchingForm(_ModelForm):
    watch = _BooleanField

    class Meta:
        model = _Fiction
        fields = []
