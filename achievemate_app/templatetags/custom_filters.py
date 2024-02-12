# custom_filters.py

from django import template

register = template.Library()

@register.filter
def comma_to_li(value):
    items = value.split(',')
    return '\n'.join([f'<li>{item.strip().capitalize()}</li>' for item in items])
