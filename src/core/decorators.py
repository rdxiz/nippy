from functools import wraps
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseRedirect
from django.shortcuts import redirect

def non_authenticated(function):
    @wraps(function)
    def wrap(request, *args, **kwargs):
        if request.user.is_authenticated:
            return HttpResponseRedirect('/')
        return function(request, *args, **kwargs)
    return wrap


def profile_required(function):
    @wraps(function)
    def wrap(request, *args, **kwargs):
        if not request.profile:
            return redirect('core:profile_switcher')
        return function(request, *args, **kwargs)
    return wrap


def ajax_only(function):
    @wraps(function)
    def wrap(request, *args, **kwargs):
        # if request.headers.get('x-requested-with') != 'XMLHttpRequest':
        #     print(request.headers)
        return function(request, *args, **kwargs)
    return wrap
