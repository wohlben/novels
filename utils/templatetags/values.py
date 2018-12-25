from django import template

register = template.Library()


@register.filter(name="values")
def values(qs, values):
    return qs.values(*values.split())
