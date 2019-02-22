from django.conf.urls import url
from planet import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    url(r'^$', views.home, name='home'),
    url(r'^about/$', views.about, name='about'),
    url(r'^hall_of_fame/$', views.hall_of_fame, name='leaderboard'),

    url(r'^register/$', views.register, name='register'),
    url(r'^login/$', views.user_login, name='login'),

    url(r'^contact/', views.contact, name='contact'),
    url(r'^logout/$', views.user_logout, name='logout'),

    url(r'^(?P<username_slug>[\w\-]+)/$',
        views.account, name='account'),
    url(r'^(?P<username_slug>[\w\-]+)/create-system/$',
        views.create_system, name='create_system'),
    url(r'^(?P<username_slug>[\w\-]+)/(?P<system_slug>[\w\-]+)/$',
        views.view_system, name='view_system'),    


    url(r'^(?P<username_slug>[\w\-]+)/(?P<system_slug>[\w\-]+)/create-planet/$',views.create_planet,
        name ='create_planet'),
    url(r'^(?P<username_slug>[\w\-]+)/(?P<system_slug>[\w\-]+)/(?P<planet_slug>[\w\-]+)/$', views.view_planet,
        name='view_planet'),
    url(r'^(?P<username_slug>[\w\-]+)/(?P<system_slug>[\w\-]+)/(?P<planet_slug>[\w\-]+)/edit/$', views.edit_planet,
        name='edit_planet'),


]
