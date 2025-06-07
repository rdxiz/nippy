from django import template
from django.db.models.functions import datetime
from django.templatetags.static import static
from django.urls import reverse
from django.utils.timezone import now, timedelta

register = template.Library()
@register.filter(name='avatar')
def get_avatar(profile , width : int):
    return profile.avatar.url if profile.avatar else static('img/silhouette100.png')



@register.simple_tag(name='fallback_thumb')
def get_thumbnail(thumbnail):
    return thumbnail.url if thumbnail else static('img/vi/default.jpg')


@register.filter
def time_ago(value):
    if not isinstance(value, datetime.datetime):
        return value

    now_time = now()
    delta = now_time - value

    seconds = delta.total_seconds()
    minutes = seconds / 60
    hours = minutes / 60
    days = hours / 24
    months = days / 30
    years = days / 365

    if seconds < 60:
        return f"{int(seconds)} seconds ago"
    elif minutes < 60:
        return f"{int(minutes)} minutes ago"
    elif hours < 24:
        return f"{int(hours)} hours ago"
    elif days < 30:
        return f"{int(days)} days ago"
    elif months < 12:
        return f"{int(months)} months ago"
    else:
        return f"{int(years)} years ago"


@register.filter
def filesizeformat(value):
    """
    Converts bytes to a human-readable format (MB, GB).
    """
    if value is None:
        return ''
    value = float(value)
    # Define thresholds for conversion
    kb = 1024
    mb = kb * 1024
    gb = mb * 1024

    if value >= gb:
        return f'{value / gb:.2f} GB'
    elif value >= mb:
        return f'{value / mb:.2f} MB'
    elif value >= kb:
        return f'{value / kb:.2f} KB'
    else:
        return f'{value:.2f} bytes'
    
@register.filter
def timeformat(seconds):
    """
    Converts seconds to a human-readable format (seconds, minutes, hours).
    """
    if seconds is None:
        return ''
    
    seconds = int(seconds)
    
    if seconds < 60:
        return f'{seconds} seconds'
    elif seconds < 3600:
        minutes = seconds // 60
        return f'{minutes} minute{"s" if minutes > 1 else ""}'
    else:
        hours = seconds // 3600
        return f'{hours} hour{"s" if hours > 1 else ""}'


@register.filter
def format_duration(seconds):
    duration = timedelta(seconds=seconds)
    hours, remainder = divmod(duration.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    
    if duration.days > 0 or hours > 0:
        return f"{hours:02}:{minutes:02}:{seconds:02}"
    else:
        return f"{minutes:02}:{seconds:02}"
