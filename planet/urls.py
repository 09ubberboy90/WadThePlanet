from django.conf.urls import url
from planet import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    url(r'^$', views.home, name='home'),
    url(r'^about/$', views.about, name='about'),
    url(r'^leaderboard/$', views.leaderboard, name='leaderboard'),

    url(r'^register/$', views.register, name='register'),
    url(r'^login/$', views.user_login, name='login'),
    url(r'^search/$', views.search, name='search'),

    url(r'^contact/', views.contact, name='contact'),
    url(r'^logout/$', views.user_logout, name='logout'),

    # /<username>/*
    url(r'^(?P<username>[A-Za-z0-9]+)/edit/$',
        views.edit_user, name='edit_user'),
    url(r'^(?P<username>[A-Za-z0-9]+)/delete/$',
        views.delete_user, name='delete_user'),
    url(r'^(?P<username>[A-Za-z0-9]+)/create-system/$',
        views.create_system, name='create_system'),
    url(r'^(?P<username>[A-Za-z0-9]+)/$',
        views.view_user, name='view_user'),

    # /<username>/<systemname>/*
    url(r'^(?P<username>[A-Za-z0-9]+)/(?P<systemname>[A-Za-z0-9]+)/create-planet/$',
        views.create_planet, name='create_planet'),
    url(r'^(?P<username>[A-Za-z0-9]+)/(?P<systemname>[A-Za-z0-9]+)/$',
        views.view_system, name='view_system'),
    url(r'^(?P<username>[A-Za-z0-9]+)/(?P<systemname>[A-Za-z0-9]+)/delete/$',
        views.delete_system, name='delete_system'),

    # /<username>/<systemname>/<planetname>
    url(r'^(?P<username>[A-Za-z0-9]+)/(?P<systemname>[A-Za-z0-9]+)/(?P<planetname>[A-Za-z0-9]+)/edit/$',
        views.edit_planet, name='edit_planet'),
    url(r'^(?P<username>[A-Za-z0-9]+)/(?P<systemname>[A-Za-z0-9]+)/(?P<planetname>[A-Za-z0-9]+)/$',
        views.view_planet, name='view_planet'),
    url(r'^(?P<username>[A-Za-z0-9]+)/(?P<systemname>[A-Za-z0-9]+)/(?P<planetname>[A-Za-z0-9]+)/delete/$',
        views.delete_planet, name='delete_planet'),
]
