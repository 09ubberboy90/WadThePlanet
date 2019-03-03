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
    }
    return render(request, 'planet/home.html', context=context)


def view_user(request: HttpRequest, username: str) -> HttpResponse:
    user = PlanetUser.objects.get(username=username)
    return render(request, 'planet/view_user.html', {'username': user})


def edit_user(request: HttpRequest, username: str) -> HttpResponse:
    pass

def view_system(request: HttpRequest, username: str, systemname: str) -> HttpResponse:
    pass

def view_planet(request: HttpRequest, username: str, systemname: str, planetname: str) -> HttpResponse:
    '''
    View a specific planet.
    GET: Render editor.html in readonly mode, render comments.html
    POST: Post the given comment form
    '''
    planet = Planet.objects.get(name=planetname, user__username=username, solarSystem__name=systemname)

    context = {
        'comments': Comment.objects.filter(planet=planet),
        'planet': planet,
    }

    if request.user.is_authenticated:
        # Display and handle comment form only if an user is logged in
        if request.method == 'POST':
            # POST: upload the posted comment
            form = CommentForm(request.POST)

            comment = form.save(commit=False)
            comment.user = request.user
            comment.planet = planet
            comment.save()  # Commit to DB
        else:
            # GET: Display an empty comment form
            form = CommentForm()

        context['comment_form'] = form
    else:
        # No comment form for logged-out users
        context['comment_form'] = None

    return render(request, 'planet/view_planet.html', context=context)

def edit_planet(request: HttpRequest, username: str, systemname: str, planetname: str) -> HttpResponse:
    '''
    Edit a specific planet.
    GET: Render editor.html in read + write mode
    POST: Post the modified planet texture (done via AJAX from editor.js)
    '''
    planet = Planet.objects.get(name=planetname, user__username=username, solarSystem__name=systemname)

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
        }
        return render(request, 'planet/edit_planet.html', context=context)

def create_system(request: HttpRequest, username: str) -> HttpResponse:
    pass

def create_planet(request: HttpRequest, username: str, systemname: str) -> HttpResponse:
    pass


def register(request: HttpRequest) -> HttpResponse:
    if request.method == 'POST':
        f = RegistrationForm(request.POST)
        if f.is_valid():
            f.save()
            username=f.cleaned_data['username']
            password=f.cleaned_data['password']
            user = auth.authenticate(username=username, password=password)
            auth.login(request, user)
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
                messages.error(request, 'Username and Password do not match')
                render(request, 'planet/user_login.html',
                       {'user_form': f})
    else:
        f = LoggingForm()
    return render(request, 'planet/user_login.html', {'user_form': f})
    
def search(request):
#	result_list = []
#	if request.method == 'GET':
#		query = request.GET['query'].strip()
#		if query:
            # Run our Webhose search function to get the results list!
#			result_list = run_query(query)

    result_list = run_query(request.GET['query'].strip())
    return render(request, 'planet/search.html', {'result_list': result_list})
    
@login_required
def user_logout(request):
    # Since we know the user is logged in, we can now just log them out.
    logout(request)
    # Take the user back to the homepage.
    return redirect('home')

