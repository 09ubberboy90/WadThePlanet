from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from planet.models import Planet, PlanetUser

# Register your models here.
admin.site.register(PlanetUser)
admin.site.register(Planet)
