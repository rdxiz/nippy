import traceback
from discord_webhook import DiscordWebhook
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.utils.deprecation import MiddlewareMixin
from django.utils.html import linebreaks
from django.http.response import Http404
from core.const import SESSION_KEY_PROFILE
from core.models import Profile, ServerError
from nippy import settings


class AppMiddleware(MiddlewareMixin):
    def process_request(self, request):
        profile_id = request.session.get(SESSION_KEY_PROFILE)
        if profile_id:
            try:
                request.profile = Profile.objects.filter(id=profile_id).first()
            except Profile.DoesNotExist:
                request.profile = None
        else:
            request.profile = None

        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0]
        else:
            ip = request.META.get("REMOTE_ADDR")

        request.remote_addr = ip
        request.remote_addr_ver = 6 if ":" in ip else 4

    def process_exception(self, request, exception):
        if not settings.DEBUG:
            if exception:
                if type(exception) in [Http404, PermissionDenied]:
                    raise exception
                ServerError.objects.create(
                    author=request.profile,
                    url=request.build_absolute_uri(),
                    error=repr(exception)[:1000],
                    traceback=traceback.format_exc()[:10000],
                )

            return HttpResponse(
                "Oops, there was a server error processing this request :(", status=500
            )
