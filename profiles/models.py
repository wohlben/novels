from django.db import models
from novels.models import Fiction
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    
    @property
    def watching(self):
        return Fiction.objects.filter(watching=self).order_by('title')
