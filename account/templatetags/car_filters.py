from django import template

register = template.Library()

@register.filter
def miles(value):
    try:
        return f"{int(value):,}"
    except (ValueError, TypeError):
        return value