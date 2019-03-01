from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from planet.models import Planet, PlanetUser, SolarSystem
#from planet.forms import CustomUserCreationForm

# Register your models here.
admin.site.register(PlanetUser)
admin.site.register(Planet)
admin.site.register(SolarSystem)
