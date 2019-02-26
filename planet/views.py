from django.shortcuts import render
from django.http import HttpRequest, HttpResponse
from planet.models import Planet
from planet.forms import *
from django.contrib import messages


# Create your views here.


def home(request: HttpRequest) -> HttpResponse:
    return render(request, 'planet/home.html')

def test(request: HttpRequest) -> HttpResponse:
    # FIXME(Paolo): Test!
    context = {
        'planet': Planet.objects.get(pk=1),
    }
    return render(request, 'planet/test.html', context=context)


def register(request: HttpRequest) -> HttpResponse:
    if request.method == 'POST':
        f = CustomUserCreationForm(request.POST)
        if f.is_valid():
            f.save()
            messages.success(request, 'Account created successfully')
            return redirect('register')

    else:
        f = CustomUserCreationForm()
    return render(request, 'planet/register.html', {'user_form': f})


def user_login(request: HttpRequest) -> HttpResponse:
    # FIXME(Florent): Implement
    return render(request, 'planet/user_login.html')
