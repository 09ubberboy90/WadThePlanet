from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Profile(models.Model):
    # This line is required. Links UserProfile to a User model instance.
    user = models.OneToOneField(User)
    # The additional attributes we wish to include.
    picture = models.ImageField(upload_to='profile_images', blank=True)

    def __str__(self) -> str:
        return self.user.username

class Planet(models.Model):
    # An unique numeric id for each planet
    id = models.AutoField(null=False, primary_key=True)
    # The name of the planet
    name = models.CharField(null=False, max_length=50)
    # The planet's texture (as painted by the user).
    texture = models.ImageField(null=False, upload_to='planets')

    def __str__(self) -> str:
        return self.name
