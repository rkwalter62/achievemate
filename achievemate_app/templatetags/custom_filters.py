# custom_filters.py

from django import template
from datetime import datetime
from django.utils import timezone
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

@register.filter(name='remaining_days')
def remaining_days(due_date):
    if not due_date:
        return None
    # Make datetime.now() timezone-aware
    now = timezone.now()
    # Calculate the remaining days
    remaining_days = (due_date - now).days
    return remaining_days

@register.filter(name='absolute_value')
def absolute_value(value):
    return abs(value)