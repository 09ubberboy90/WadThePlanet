import base64
import re
import logging
from django.shortcuts import render
from django.http import HttpRequest, HttpResponse, HttpResponseBadRequest
from planet.models import Planet
from planet.forms import *
from django.contrib import messages

# ======================== Utilities ===========================================

logger = logging.getLogger(__name__)

# ======================== Views ===============================================

def home(request: HttpRequest) -> HttpResponse:
    return render(request, 'planet/home.html')

def test(request: HttpRequest) -> HttpResponse:
    # FIXME(Paolo): Test!
    planet = Planet.objects.get(pk=1)
    if request.method == 'POST':
        # POST: upload the newly-edited image
        # Expects a {data: "<base64-encoded image from Canvas>"} in the POST request
        # FIXME(Paolo): Resize image if needed, reject wrongly-sized images!
        logger.debug(f'Planet{planet.id}: saving texture...')
        try:
            planet.texture.save(f'{planet.id}.jpg', request.FILES['texture'])  # See the AJAX request in editor.js:onSave() 
            planet.save()
            logger.debug(f'Planet{planet.id}: texture saved')
            return HttpResponse('saved')
        except Exception as e:
            logger.error(f'Planet{planet.id}: error saving texture: {repr(e)}')
            return HttpResponseBadRequest('error') 
    else:
        # POST or GET: launch the editor
        context = {
            'planet': planet,
            'editing_enabled': False,
            'cam_controls_enabled': False,
            'spin_speed': 0.20,
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
