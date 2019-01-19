from django import template  # pragma: no cover

register = template.Library()  # pragma: no cover


@register.filter(name="sub")  # pragma: no cover
def subtract(first, second):
    return first - second
