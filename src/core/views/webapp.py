from django.shortcuts import render
from django.views import View


class WebAppView(View):
    def get(self, request, *args, **kwargs):
        return render(request, "index.html", {})
