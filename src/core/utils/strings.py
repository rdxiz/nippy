
from django.utils.timezone import timedelta
from django.utils.translation import gettext as _


def rate_limit_msg(diff):
    if diff < timedelta(minutes=1):
        seconds = diff.seconds
        data = {'count': seconds}
        return _("You're being rate limited, wait %(count)s seconds and try again.") % data if seconds > 1 else _("You're being rate limited, wait a second and try again.")
    elif diff < timedelta(hours=1):
        minutes = diff.seconds // 60
        data = {'count': minutes}
        return _("You're being rate limited, wait %(count)s minutes and try again.") % data if minutes > 1 else _("You're being rate limited, wait a minute and try again.")
    elif diff < timedelta(days=1):
        hours = diff.seconds // 3600
        data = {'count': hours}
        return _("You're being rate limited, wait %(count)s hours and try again.") % data if hours > 1 else _("You're being rate limited, wait a hour and try again.")
    elif diff < timedelta(days=30):
        days = diff.days
        data = {'count': days}
        return _("You're being rate limited, wait %(count)s days and try again.") % data if days > 1 else _("You're being rate limited, wait a day and try again.")
