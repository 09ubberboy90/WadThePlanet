import base64
import re
import logging
from django.shortcuts import render
from django.http import HttpRequest, HttpResponse, HttpResponseBadRequest
from planet.webhose_search import run_query
from planet.models import Planet, Comment, PlanetUser
from planet.forms import LoggingForm, RegistrationForm, CommentForm
from django.contrib import messages, auth
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout


# ======================== Utilities ===========================================

logger = logging.getLogger(__name__)

# ======================== Views ===============================================


def home(request: HttpRequest) -> HttpResponse:
    # FIXME(Paolo): Test!
    #planet = Planet.objects.get(pk=1)
    planet = Planet.objects.get_or_create(name="planet2")[0]

    context = {
        'planet': planet,
        'editing_enabled': False,
        'cam_controls_enabled': False,
        'spin_speed': 0.15,
    }
    return render(request, 'planet/home.html', context=context)


def view_planet(request: HttpRequest) -> HttpResponse:
    # FIXME(Paolo): Test!
    user = PlanetUser.objects.get(pk=1)
    planet = Planet.objects.get(pk=1)

    if request.method == 'POST':
        # POST: upload the posted comment
        form = CommentForm(request.POST)

        comment = form.save(commit=False)
        comment.user = user
        comment.planet = planet
        comment.save()  # Commit to DB
    else:
        form = CommentForm()

    context = {
        'comment_form': form,
        'comments': Comment.objects.filter(user=user, planet=planet),
    }
    return render(request, 'planet/test.html', context=context)


def edit_planet(request: HttpRequest) -> HttpResponse:
    # FIXME(Paolo): Test!
    planet = Planet.objects.get(pk=1)
    if request.method == 'POST':
        # POST: upload the newly-edited image
        # Expects a {data: "<base64-encoded image from Canvas>"} in the POST request
        # FIXME(Paolo): Resize image if needed, reject wrongly-sized images!
        logger.debug(f'Planet{planet.id}: saving texture...')
        try:
            # See the AJAX request in editor.js:onSave()
            planet.texture.save(f'{planet.id}.jpg', request.FILES['texture'])
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
            'editing_enabled': True,
            'cam_controls_enabled': True,
            'spin_speed': 0.0,
        }
        return render(request, 'planet/test.html', context=context)


def register(request: HttpRequest) -> HttpResponse:
    if request.method == 'POST':
        f = RegistrationForm(request.POST)
        if f.is_valid():
            f.save()
            messages.success(request, 'Account created successfully')
            return redirect('home')
    else:
        f = RegistrationForm()
    return render(request, 'planet/register.html', {'user_form': f})


def user_login(request: HttpRequest) -> HttpResponse:
    if request.method == 'POST':
        f = LoggingForm(request.POST)
        if f.is_valid():
            username = f.clean_username()
            password = f.clean_password()
            user = auth.authenticate(username=username, password=password)
            if user:
                auth.login(request, user)
                return redirect('home')
            else:
                render(request, 'planet/user_login.html',
                       {'user_form': f, 'error': True})
    else:
        f = LoggingForm()
    return render(request, 'planet/user_login.html', {'user_form': f, 'error': False})


def search(request):
	result_list = []
	if request.method == 'GET':
		query = request.GET['query'].strip()
		if query:
			# Run our Webhose search function to get the results list!
			result_list = run_query(query)
	return render(request, 'planet/search.html', {'result_list': result_list})


@login_required
def user_logout(request):
    # Since we know the user is logged in, we can now just log them out.
    logout(request)
    # Take the user back to the homepage.
    return redirect('home')

