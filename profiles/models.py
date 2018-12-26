from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    COLOR_CHOICES = (
        ("cerulean", "cerulean"),
        ("cosmo", "cosmo"),
        ("cyborg", "cyborg"),
        ("darkly", "darkly (default)"),
        ("flatly", "flatly"),
        ("journal", "journal"),
        ("litera", "litera"),
        ("lumen", "lumen"),
        ("lux", "lux"),
        ("materia", "materia"),
        ("minty", "minty"),
        ("pulse", "pulse"),
        ("pulse", "pulse"),
        ("sandstone", "sandstone"),
        ("simplex", "simplex"),
        ("sketchy", "sketchy"),
        ("slate", "slate"),
        ("solar", "solar"),
        ("spacelab", "spacelab"),
        ("superhero", "superhero"),
        ("united", "united"),
        ("yeti", "yeti"),
    )

    internal_links = models.BooleanField(default=False)
    color_theme = models.CharField(
        default="darkly", choices=COLOR_CHOICES, max_length=50
    )
