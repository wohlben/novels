from django import template  # pragma: no cover

register = template.Library()  # pragma: no cover


@register.filter(name="values")  # pragma: no cover
def values(qs, values):
    return qs.values(*values.split())
