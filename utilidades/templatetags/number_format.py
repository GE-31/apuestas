from decimal import Decimal, InvalidOperation

from django import template


register = template.Library()


@register.filter
def odds2(value):
    try:
        number = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        return "-"
    return f"{number:.2f}"


@register.filter
def decimal4(value):
    try:
        number = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        return "0.0000"
    return f"{number:.4f}"
