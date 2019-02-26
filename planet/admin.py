from django.contrib import admin

from planet.models import Planet, Profile

# Register your models here.
admin.site.register(Profile)
admin.site.register(Planet)