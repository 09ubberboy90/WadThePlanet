import base64
import re
import logging
from django.shortcuts import render
from django.http import HttpRequest, HttpResponse, HttpResponseBadRequest
from planet.models import Planet
from planet.forms import *

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
            planet.texture.save(f'{planet.id}.png', request.FILES['texture'])  # See the AJAX request in editor.js:onSave() 
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
        }
        return render(request, 'planet/test.html', context=context)


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
