from django.forms import ModelForm
from .models import User


class ProfileForm(ModelForm):
    class Meta:
        model = User
        fields = ("color_theme", "internal_links", "enable_login_token")
