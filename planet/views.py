import base64
import re
import logging
from django.shortcuts import render
from django.http import HttpRequest, HttpResponse, HttpResponseBadRequest, HttpResponseForbidden ,HttpResponseNotFound
from planet.webhose_search import run_query
from planet.models import Planet, Comment, PlanetUser, SolarSystem
from planet.forms import LoggingForm, RegistrationForm, CommentForm, SolarSystemForm, EditUserForm
from django.contrib import messages, auth
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.http import Http404


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
    try:
        user = PlanetUser.objects.get(username=username)
    except PlanetUser.DoesNotExist:
        raise Http404(username)
    return render(request, 'planet/view_user.html', {'username': user})


def edit_user(request: HttpRequest, username: str) -> HttpResponse:
    '''
    Edits request.user.
    GET: Render the editing form
    POST: Apply the edited fields
    '''
    if username != request.user.username:
        return HttpResponseForbidden(f'You need to log in as {username} to edit his profile')

    if request.method == 'POST':
        form = EditUserForm(request.POST, user_id=request.user.id)
        if form.is_valid():
            # Change only the data that was input by the user
            if form.cleaned_data['username']:
                request.user.username = form.cleaned_data['username']
            if form.cleaned_data['password']:
                # NOTE: If you don't set_password, it gets saved as plaintext!!
                request.user.set_password(form.cleaned_data['password'])
            if form.cleaned_data['avatar']:
                user.avatar = form.cleaned_data['avatar']
            request.user.save()
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
        system = SolarSystem.objects.get(name=systemname, user__username=username)
        planets = Planet.objects.filter(solarSystem__name=systemname)
        try:
            user = PlanetUser.objects.get(username=username)
            #FiXME : Implement me
        except PlanetUser.DoesNotExist:
            raise Http404()
        return render(request, 'planet/view_system.html', {'system': system, 'planets': planets })


def view_planet(request: HttpRequest, username: str, systemname: str, planetname: str) -> HttpResponse:
    '''
    View a specific planet.
    GET: Render editor.html in readonly mode, render comments.html
    POST: Post the given comment form
    '''
    try:
        planet = Planet.objects.get(name=planetname, user__username=username, solarSystem__name=systemname)
        solarSystem = SolarSystem.objects.get(name=systemname)
    except Planet.DoesNotExist:
        raise Http404()

    if planet.user != request.user and not planet.visibility:
        return HttpResponseForbidden(f'This planet is hidden')

    context = {
        'comments': Comment.objects.filter(planet=planet),
        'planet': planet,
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

            comment = form.save(commit=False)
            comment.user = request.user
            comment.planet = planet

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
    planet = Planet.objects.get(name=planetname, user__username=username, solarSystem__name=systemname)

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
        return HttpResponseForbidden(f'You not to be logged in as {username}')

    if request.method == 'POST':
        form = SolarSystemForm(request.user)
        if form.is_valid():
            system = form.save(commit=False)
            system.user = request.user
            system.save()
            return redirect('view_system')
    else:
        form = SolarSystemForm(request.user)
    return render(request, 'planet/create_system.html', {'form': form})


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

def search(request, count=100):

    result_list = run_query(request.GET['query'].strip(), count)
    return render(request, 'planet/search.html', {'result_list': result_list})

@login_required
def user_logout(request):
    # Since we know the user is logged in, we can now just log them out.
    logout(request)
    # Take the user back to the homepage.
    return redirect('home')
