import base64
import re
import logging
import os
from typing import List
from django.shortcuts import render
from django.http import HttpRequest, HttpResponse, HttpResponseBadRequest, HttpResponseForbidden ,HttpResponseNotFound
from planet.webhose_search import run_query
from planet.models import Planet, Comment, PlanetUser, SolarSystem
from planet.forms import LoggingForm, RegistrationForm, CommentForm, SolarSystemForm, EditUserForm, LeaderboardForm, PlanetForm
from django.contrib import messages, auth
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.http import Http404


# ======================== Utilities ===========================================

logger = logging.getLogger(__name__)  # A utility logger
HOST = 'http://wdp.pythonanywhere.com/'  # The URL of the website when hosted.
                                         # Required for social media sharing buttons to work.

def get_mvps(model: 'Model', criteria: str='-score') -> List:
    '''Gets the object[s] with the best `criteria` from the given model,
    excluding those that have `visibility=False`.
    '''
    return model.objects.exclude(visibility=False).order_by(criteria)

# ======================== Views ===============================================


def home(request: HttpRequest) -> HttpResponse:
    '''
    Shows an index/landing page, showcasing the highest-scoring planet.
    GET: Renders the page.
    '''
    mvp_planet = get_mvps(Planet)[0]
    context = {
        'planet': mvp_planet,
    }
    return render(request, 'planet/home.html', context=context)


def leaderboard(request: HttpRequest) -> HttpResponse:
    '''
    Shows the leaderboard page, sorting all planets and systems by certain criteria.
    GET: Renders the page.
    POST: Posts the form used to choose the sorting method. 
    '''
    context = {}

    result = '-score'
    if request.method == 'POST':
        form = LeaderboardForm(request.POST)
        if form.is_valid():
            result = form.cleaned_data['choice']
            if result != "name":
                result = '-' + result
    else:
        form = LeaderboardForm()

    planets = get_mvps(Planet, result)
    solars = get_mvps(SolarSystem, result)

    context['form'] = form
    context['planets'] = planets
    context['solars'] = solars
    context['page'] = 'leaderboard'
    return render(request, 'planet/leaderboard.html',context= context)

def view_user(request: HttpRequest, username: str) -> HttpResponse:
    '''
    Shows the profile of the user named `username`.
    GET: Renders the page.
    '''
    try:
        user = PlanetUser.objects.get(username=username)
        planets = Planet.objects.filter(user__username=username)
        solar = SolarSystem.objects.filter(user__username=username)
    except (PlanetUser.DoesNotExist,Planet.DoesNotExist,SolarSystem.DoesNotExist):
        raise Http404(username)

    context = {
        'username': user,
        'planets': planets,
        'solars': solar,
        'page': 'view'
    }
    return render(request, 'planet/view_user.html', context)

@login_required
def delete_user(request: HttpRequest, username: str) -> HttpResponse:
    '''
    Deletes the currently logged-in user.
    Only a logged-in user is allowed to delete its own account, so `username` must match `request.user.username`.
    POST: Deletes the user, his planets, his solar systems and the planets in his
          solar systems (even if they are by other users). Returns an error if the
          name does not match.
    GET: Returns an error, only POST allowed.
    '''
    try:
        if request.method != 'POST':
            raise ValueError()

        if request.user.username == username:
            u = PlanetUser.objects.get(username=request.user.username)
            planets = Planet.objects.filter(user__username=username)
            solars = SolarSystem.objects.filter(user__username=username)
            for planet in planets:
                planet.delete()
            for solar in solars:
                system_planet = Planet.objects.filter(solarSystem__id= solar.id)
                for planet in system_planet:
                    planet.delete()
                solar.delete()
            if(u.avatar):
                os.remove(u.avatar.url)
            u.delete()
        else:
            message = 'A hacker discovered you tried to get '+ username + ' killed and now threatens to blackmail you'
            return render(request, 'planet/error.html', {'error': message})

    except Exception as e:
        message = 'A fleet of enemy has intercepted your message and refuses to surrender it\n So please try again'
        #message += e
        return render(request, 'planet/error.html', {'error': message})

    return redirect('home')

@login_required
def delete_system(request: HttpRequest, username: str, systemname: str) -> HttpResponse:
    '''
    Deletes the current system.
    Only a logged-in user is allowed to delete its own system, so `solar.user.username` must match `request.user.username`.
    POST: Deletes his solar system and the planets in it
    GET: Returns an error, only POST allowed.
    '''
    try:
        if request.method != 'POST':
            raise ValueError()
        solar = SolarSystem.objects.get(name=systemname)
        if request.user.username == solar.user.username:
            planets = Planet.objects.filter(solarSystem__name=systemname)
            for planet in planets:
                planet.delete()
            solar.delete()
        else:
            message = 'A hacker discovered you tried to get ' + systemname + ' destroy and now threatens to blackmail you'
            return render(request, 'planet/error.html', {'error': message})
    except Exception as e:
        message = 'A fleet of enemy has intercepted your message and refuses to surrender it\n So please try again'
        #message += e
        return render(request, 'planet/error.html', {'error': message})

    return redirect('home')


@login_required
def delete_planet(request: HttpRequest, username: str, systemname: str, planetname: str) -> HttpResponse:
    '''
    Deletes the current planet.
    Only a logged-in user is allowed to delete its own planet, so `username` must match `request.user.username`.
    POST: Deletes the user, his planets, his solar systems and the planets in his
          solar systems (even if they are by other users). Returns an error if the
          name does not match.
    GET: Returns an error, only POST allowed.
    '''
    try:
        if request.method != 'POST':
            raise ValueError()

        planet = Planet.objects.get(name=planetname)
        if request.user.username == planet.user.username:
            planet.delete()
        else:
            message = 'A hacker discovered you tried to get ' + \
                planetname + ' destroyed and now threatens to blackmail you'
            return render(request, 'planet/error.html', {'error': message})

    except Exception as e:
        message = 'A fleet of enemy has intercepted your message and refuses to surrender it\n So please try again'
        #message += e
        return render(request, 'planet/error.html', {'error': message})

    return redirect('home')

@login_required
def edit_user(request: HttpRequest, username: str) -> HttpResponse:
    '''
    Edits the currently-logged-in user.
    Only a logged-in user is allowed to edit its own account, so `username` must match `request.user.username`.
    GET: Renders the editing form.
    POST: Apply the edits to `request.user`.
    '''
    if username != request.user.username:
        return HttpResponseForbidden(f'You need to log in as {username} to edit his profile')

    if request.method == 'POST':
        form = EditUserForm(request.POST, request.FILES, user_id=request.user.id)
        if form.is_valid():
            f = form.save()
            # Change only the data that was input by the user
            f.save()
            if(form.cleaned_data['username']):
                return redirect('view_user', form.cleaned_data['username'])
            else:
                return redirect('view_user' ,request.user.username)
    else:
        form = EditUserForm(user_id=request.user.id)

    context = {
        'user_form': form,
    }
    return render(request, 'planet/edit_user.html', context)


def view_system(request: HttpRequest, username: str, systemname: str) -> HttpResponse:
    '''
    Renders some information and the list of planets contained in a solar system.
    The solar system should have been created by `username` and be named `systemname`.
    GET: Renders the page.
    '''
    try:
        system = SolarSystem.objects.get(name=systemname, user__username=username)
        planets = Planet.objects.filter(solarSystem=system)
    except SolarSystem.DoesNotExist:
        raise Http404()

    return render(request, 'planet/view_system.html', {'system': system, 'planets': planets })


def view_planet(request: HttpRequest, username: str, systemname: str, planetname: str) -> HttpResponse:
    '''
    Renders a 3D view of a specific planet, with a form to post comments and ratings plus share the page.

    The planet should be named `planetname`, and have been created inside a system `systemname`.
    The system should have been created by `username`.

    GET: Renders `editor.html` in readonly mode; the camera can be rotated/zoomed but painting is not possible.
         Renders `comments.html` in read/write mode; comments can be posted.
    POST: Post the comment form.
    '''
    try:
        planet = Planet.objects.get(name=planetname, solarSystem__user__username=username, solarSystem__name=systemname)
        solarSystem = planet.solarSystem
    except Planet.DoesNotExist:
        raise Http404()

    if planet.user != request.user and not planet.visibility:
        return HttpResponseForbidden(f'This planet is hidden')

    context = {
        'comments': Comment.objects.filter(planet=planet),
        'planet': planet,
        'this_page': HOST + request.path, # Required by social media buttons
    }

    if request.user.is_authenticated:
        # Display and handle comment form only if an user is logged in
        if request.method == 'POST':  # POST: upload the posted comment
            form = CommentForm(request.POST)

            #If there is already a comment for this planet with this user name, modify existing comment
            preexisting = Comment.objects.filter(planet=planet, user=request.user)
            if preexisting.count() > 0:
                form.instance = preexisting[0]

            if form.is_valid():
                comment = form.save(request.user,planet)
                comment.save()  # Commit to DB. This will also modify the ratings for the parent solar system and planet.

        else:
            # GET: Display an empty comment form
            form = CommentForm()

        context['comment_form'] = form
    else:
        # No comment form for logged-out users
        context['comment_form'] = None

    return render(request, 'planet/view_planet.html', context=context)

@login_required
def edit_planet(request: HttpRequest, username: str, systemname: str, planetname: str) -> HttpResponse:
    '''
    Renders a 3D editor for the given planet, allowing the user to paint it.

    The planet should be named `planetname`, and have been created inside a system `systemname`.
    The system should have been created by `username`.
    Only the logged-in user can edit his own planets.

    GET: Render editor.html in read + write mode
    POST: Post the modified planet texture (done via AJAX from editor.js)
    '''
    try:
        planet = Planet.objects.get(name=planetname, solarSystem__user__username=username, solarSystem__name=systemname)
    except Planet.DoesNotExist:
        raise Http404()

    if planet.user != request.user:
        return HttpResponseForbidden(f'You must be logged in as {planet.user.username} to edit this planet!')

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
    '''
    Renders a form to create a new solar system.
    Only the logged-in user can create solar systems under his name.

    GET: Renders the creation form.
    POST: Validates the form and creates the new system if successful.
    '''
    if request.user.username != username:
        return HttpResponseForbidden(f'You need to be logged in as {username}')

    if request.method == 'POST':
        form = SolarSystemForm(request.POST)

        if form.is_valid():
            if SolarSystem.objects.filter(user=request.user, name=form.cleaned_data['name']).count() > 0:
                messages.error(request, 'You have already created a system with the same name')
            else:
                system = form.save(commit=False)
                system.user = request.user
                system.views = 0
                system.save()
                return redirect('view_system', username=username, systemname=system.name)
        else:
            messages.error(request, '')
            print(form.errors)
    else:
        form = SolarSystemForm()

    return render(request, 'planet/create_system.html', {'form': form, 'username': username})


@login_required
def create_planet(request: HttpRequest, username: str, systemname: str) -> HttpResponse:
    '''
    Renders a form to create a new planet.
    Only the logged-in user can create a planet under his name, but he can create
    it under anyone's (public) solar systems.

    GET: Renders the creation form.
    POST: Validates the form and creates the new planet if successful.
    '''
    if request.method == 'POST':
        form = PlanetForm(request.POST)
        if form.is_valid():
            system = SolarSystem.objects.get(user__username=username, name=systemname)
            planet = form.save(commit=False)
            planet.user = request.user
            planet.solarSystem = system
            planet.texture = form.generate_texture(planet.name)
            planet.score = 0
            planet.save()
            return redirect('view_planet',
                username=system.user.username, systemname=planet.solarSystem.name, planetname=planet.name)
        else:
            messages.error(request, 'Username and Password do not match')
            print(form.errors)
    else:
        form = PlanetForm()

    return render(request, 'planet/create_planet.html', {'form': form, 'username': username, 'systemname': systemname})


def register(request: HttpRequest) -> HttpResponse:
    '''
    Renders a form to register a new user.
    GET: Renders the form.
    POST: Validates the form and creates the new user if successful.
    '''
    if request.method == 'POST':
        form = RegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            f = form.save(commit=False)
            f.save()
            username=form.cleaned_data['username']
            password=form.cleaned_data['password']
            user = auth.authenticate(username=username, password=password)
            auth.login(request, user)
            return redirect('home')
    else:
        form = RegistrationForm()
    return render(request, 'planet/register.html', {'user_form': form})


def user_login(request: HttpRequest) -> HttpResponse:
    '''
    Renders a form used to handle user login.
    GET: Renders the form.
    POST: Validates the form and logs in the user if successful.
    '''
    if request.method == 'POST':
        form = LoggingForm(request.POST)
        if form.is_valid():
            username = form.clean_username()
            password = form.clean_password()
            user = auth.authenticate(username=username, password=password)
            if user:
                auth.login(request, user)
                return redirect('home')
            else:
                messages.error(request, 'Username and Password do not match')
                render(request, 'planet/user_login.html',
                       {'user_form': form})
    else:
        form = LoggingForm()
    return render(request, 'planet/user_login.html', {'user_form': form})


def search(request: HttpRequest) -> HttpResponse:
    '''
    Searchs for users, systems or planets. The search query is in ?query=
    GET: Renders the search form.
    '''
    planets, systems, users = run_query(request.GET['query'].strip())
    context = {
        'planets': planets,
        'systems': systems,
        'users': users,
    }
    return render(request, 'planet/search.html', context=context)

@login_required
def user_logout(request):
    '''
    Logs out the currently logged-in user and redirects them to the homepage.
    '''
    # Since we know the user is logged in, we can now just log them out.
    logout(request)
    # Take the user back to the homepage.
    return redirect('home')

def about(request):
    '''
    GET: Renders the about page.
    '''
    return render(request, 'planet/about.html')

def contact(request):
    '''
    GET: Renders the contact page.
    '''
    return render(request, 'planet/contact.html')
