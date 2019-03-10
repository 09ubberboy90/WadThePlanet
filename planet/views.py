import base64
import re
import logging
import os
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

logger = logging.getLogger(__name__)
HOST = 'http://wdp.pythonanywhere.com/'

# ======================== Views ===============================================


def home(request: HttpRequest) -> HttpResponse:
    # FIXME(Paolo): Test!
    #planet = Planet.objects.get(pk=1)
    planet = Planet.objects.get_or_create(name="planet2")[0]
    context = {
        'planet': planet,
    }
    return render(request, 'planet/home.html', context=context)


def leaderboard(request: HttpRequest) -> HttpResponse:
    context = {}
    if request.method == 'POST':
        form = LeaderboardForm(request.POST)
        if form.is_valid():
            result = form.cleaned_data['choice']
            if result == "name":
                planets = Planet.objects.exclude(visibility=False).order_by(result)
                solars = SolarSystem.objects.exclude(
                    visibility=False).order_by(result)
            else:
                planets = Planet.objects.exclude(visibility=False).order_by(result)[::-1]

                solars = SolarSystem.objects.exclude(visibility=False).order_by(result)[::-1]
    else:
        form = LeaderboardForm()
        solars = SolarSystem.objects.exclude(
            visibility=False).order_by('score')[::-1]
        planets = Planet.objects.exclude(
            visibility=False).order_by('score')[::-1]
    context['form'] = form
    context['planets'] = planets
    context['solars'] = solars
    context['page'] = 'leaderboard'
    return render(request, 'planet/leaderboard.html',context= context)

def view_user(request: HttpRequest, username: str) -> HttpResponse:
    try:
        user = PlanetUser.objects.get(username=username)
        planets = Planet.objects.filter(user__username=username)
        solar = SolarSystem.objects.filter(user__username=username)
    except (PlanetUser.DoesNotExist,Planet.DoesNotExist,SolarSystem.DoesNotExist):
        raise Http404(username)
    context = {'username': user, 'planets': planets, 'solars': solar, 'page':'view'}
    return render(request, 'planet/view_user.html', context)

@login_required
def delete_user(request: HttpRequest, username: str) -> HttpResponse:
    try:
        if(request.user.username == username):
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
        message += e
        return render(request, 'planet/error.html', {'error': message})

    return redirect('home')

@login_required
def edit_user(request: HttpRequest, username: str) -> HttpResponse:
    '''
    Edits request.user.
    GET: Render the editing form
    POST: Apply the edited fields
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
        View a specific solar system
        '''
        try:
            system = SolarSystem.objects.get(name=systemname, user__username=username)
            planets = Planet.objects.filter(solarSystem=system)
        except SolarSystem.DoesNotExist:
            raise Http404()
        return render(request, 'planet/view_system.html', {'system': system, 'planets': planets })


def view_planet(request: HttpRequest, username: str, systemname: str, planetname: str) -> HttpResponse:
    '''
    View a specific planet.
    GET: Render editor.html in readonly mode, render comments.html
    POST: Post the given comment form
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
        if request.method == 'POST':

            #Placeholder for modifying comments ratings
            preexisting_rating = 0
            # POST: upload the posted comment
            form = CommentForm(request.POST)
            preexisting = Comment.objects.filter(planet=planet, user=request.user)

            #If there is already a comment for this planet with this user name, modify existing comment
            if preexisting.count() > 0:
                form.instance = preexisting[0]
                #Remember old comment's rating
                preexisting_rating = preexisting[0].rating
            if form.is_valid():
                comment = form.save(request.user,planet)
                comment.save()  # Commit to DB

                #Add comment score to planet score
                planet.score += comment.rating - preexisting_rating
                planet.save()

                #Add comment score to solar system score
                solarSystem.score += comment.rating - preexisting_rating
                solarSystem.save()


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
    planet = Planet.objects.get(name=planetname, solarSystem__user__username=username, solarSystem__name=systemname)

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
    if request.user.username != username:
        return HttpResponseForbidden(f'You need to be logged in as {username}')

    if request.method == 'POST':
        form = SolarSystemForm(request.POST)

        if form.is_valid():
            system = form.save(commit=False)
            system.user = request.user
            system.views = 0
            system.save()
            return redirect('view_system', username=username, systemname=system.name)
        else:
            messages.error(request, 'Username and Password do not match')
            print(form.errors)
    else:
        form = SolarSystemForm()

    return render(request, 'planet/create_system.html', {'form': form, 'username': username})


@login_required
def create_planet(request: HttpRequest, username: str, systemname: str) -> HttpResponse:
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
    planets, systems, users = run_query(request.GET['query'].strip())

    context = {
        'planets': planets,
        'systems': systems,
        'users': users,
    }
    return render(request, 'planet/search.html', context=context)

@login_required
def user_logout(request):
    # Since we know the user is logged in, we can now just log them out.
    logout(request)
    # Take the user back to the homepage.
    return redirect('home')

def about(request):
	return render(request, 'planet/about.html')

def contact(request):
    return render(request, 'planet/contact.html')
