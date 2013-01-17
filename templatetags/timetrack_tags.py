from django import template
from django.utils.safestring import mark_safe
from datetime import date

register = template.Library()

def responsive_day(value):
    """Recieves a date object and returns the day of the week like so:
    Wed<span class="wide">nesday</span>
    This is so the remainder can be hidden if the window's too small"""
    day_text = value.strftime('%A')
    day_text = '%s<span class="wide">%s</span>' % (day_text[:3], day_text[3:])
    return mark_safe(day_text)

def responsive_date(value):
    """Recieves a date object and returns the date like so:
    1/20<span class="wide">/12</span>
    This is so the remainder can be hidden if the window's too small"""
    intro = '%d/%d' % (value.month, value.day)
    date_text = '%s<span class="wide">/%s</span>' % (intro, value.strftime('%y'))
    return mark_safe(date_text)

register.filter('responsive_day', responsive_day)
register.filter('responsive_date', responsive_date)
