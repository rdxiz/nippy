from contextlib import contextmanager
from django.utils import timezone
from django.utils.timezone import timedelta
from core.models import RateLimiter

durations = {'s': 'seconds', 'm': 'minutes', 'h': 'hours', 'd': 'days'}

def limit_key(ip, *args):
    key = ip.replace(":", "").replace(".", "")
    for arg in args:
        key = f"{key}{arg}"
    return key


@contextmanager
def limits(key, limits : list, save=True):
    for action_limit in limits:
        with limit(key, action_limit[0], action_limit[1], save=save) as diff:
            if diff:
                yield diff
                return
    yield False
    
    
@contextmanager
def limit(key, limit=100, period="30s", save=True):
    key = f"{period}{key}"
    duration = period[-1]
    period = int(period[:-1])
    now = timezone.now()
    period_start = now - timedelta(**{durations[duration]: period})
    
    try:
        rate_limit = RateLimiter.objects.get(record_id=key)
    except RateLimiter.DoesNotExist:
        if not save:
            yield False
            return
        RateLimiter.objects.create(record_id=key, count=1, last_request=now)
        yield False
        return

    if rate_limit.last_request < period_start:
        if not save:
            yield False
            return
        rate_limit.count = 1
        rate_limit.last_request = now
        rate_limit.save()
        yield False
    else:
        if rate_limit.count >= limit:
            remaining_time = rate_limit.last_request - period_start
            yield remaining_time
        else:
            if not save:
                yield False
                return
            rate_limit.count += 1
            rate_limit.last_request = now
            rate_limit.save()
            yield False
