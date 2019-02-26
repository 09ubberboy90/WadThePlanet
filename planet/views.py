from django.shortcuts import render
from django.http import HttpRequest, HttpResponse
from planet.forms import *

# Create your views here.


def home(request: HttpRequest) -> HttpResponse:
    return render(request, 'planet/home.html')

def test(request: HttpRequest) -> HttpResponse:
    # FIXME(Paolo): Test!
    return render(request, 'planet/test.html')


def register(request: HttpRequest) -> HttpResponse:
    # FIXME(Florent): Implement
    user_form = UserForm()
    profile_form = ProfileForm()
    return render(request, 'planet/register.html', {
        'user_form': user_form,
        'profile_form': profile_form
    })


def user_login(request: HttpRequest) -> HttpResponse:
    # FIXME(Florent): Implement
    return render(request, 'planet/user_login.html')
