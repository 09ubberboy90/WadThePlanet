from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from planet.models import Planet, PlanetUser
from planet.forms import CustomUserCreationForm

# Register your models here.
admin.site.register(PlanetUser,UserAdmin)
admin.site.register(Planet)
