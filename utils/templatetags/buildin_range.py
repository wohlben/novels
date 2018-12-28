from django import template  # pragma: no cover

register = template.Library()  # pragma: no cover


@register.filter(name="range")
def buildin_range(stop):
    return range(stop)
