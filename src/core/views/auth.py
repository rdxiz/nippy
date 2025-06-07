
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from core.decorators import non_authenticated, profile_required
from core.forms import SignInForm, SignUpForm


@non_authenticated
def signup(request):
    if request.method == "GET":
        return render(request, "registration/signup.html", {"form": SignUpForm()})
    form = SignUpForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect("core:signin")
    return render(request, "registration/signup.html", {"form": form})


@non_authenticated
def signin(request):
    if request.method == "GET":
        return render(request, "registration/login.html", {"form": SignInForm()})
    form = SignInForm(data=request.POST or None)
    if not form.is_valid():
        return render(request, "registration/login.html", {"form": form})
    data = form.cleaned_data
    user = authenticate(username=data['username'],password=data['password'])
    if not user:
        messages.error(request, 'Authentication failed')
        return render(request, "registration/login.html", {"form": form})
    login(request,user) 
    return redirect("core:index")


@profile_required
def signout(request):
    logout(request)
    return redirect("core:index")



