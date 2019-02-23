from django.shortcuts import render
from django.http import HttpRequest, HttpResponse

# Create your views here.


def home(request: HttpRequest) -> HttpResponse:
    return render(request, 'planet/home.html')

def test(request: HttpRequest) -> HttpResponse:
    # FIXME(Paolo): Test!
    return render(request, 'planet/test.html')