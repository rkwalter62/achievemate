# custom_filters.py

from django import template

register = template.Library()

@register.filter
def comma_to_li(value):
    items = value.split(',')
    return '\n'.join([f'<li>{item.strip().capitalize()}</li>' for item in items])

@register.filter
def remove_after_symbol(value):
    symbols = [',', '.', '-', '•']  # Add more symbols if needed
    for symbol in symbols:
        if symbol in value:
            return value.split(symbol)[0]
    return value
