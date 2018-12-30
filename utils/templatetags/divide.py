from django import template  # pragma: no cover

register = template.Library()  # pragma: no cover


@register.filter(name="divide")
def divide(number, divided_by):
    try:
        return int(number) / int(divided_by)
    except (ValueError, ZeroDivisionError, TypeError):
        return None


@register.filter(name="percent")
def percentage(number: int) -> str:
    try:
        return f"{int(number*100)} %"
    except (ValueError, TypeError):
        return ""
