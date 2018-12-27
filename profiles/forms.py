from django.forms import ModelForm, Form, CharField, Textarea
from .models import User


class BulkWatchForm(Form):
    url_list = CharField(widget=Textarea)


class ProfileForm(ModelForm):
    class Meta:
        model = User
        fields = ("color_theme", "internal_links", "enable_login_token")
