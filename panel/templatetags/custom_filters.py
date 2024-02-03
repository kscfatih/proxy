from django import template

register = template.Library()

@register.filter(name='mask_card')
def mask_card(value):
    if value and len(value) >= 4:
        return '*' * (len(value) - 4) + value[-4:]
    return value
