import logging
import os
import PIL
from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager
from django.contrib.auth.validators import ASCIIUsernameValidator
from WadThePlanet import settings
from django.contrib.auth.models import User


# ======================== Utilities ===========================================

logger = logging.getLogger(__name__)
# ======================== Models ==============================================


def content_file_name(instance, filename):
    ext = filename.split('.')[-1]
    filename = "%s.%s" % (instance.username, ext)
    return os.path.join('profile_images/', filename)

# Create your models here.*
class PlanetUser(AbstractUser):

    email = models.EmailField(
        verbose_name='email address',
        max_length=255)
    avatar = models.ImageField(
        upload_to=content_file_name, blank=True, null=True)
    REQUIRED_FIELDS = ['email']
    username_validator = ASCIIUsernameValidator()
    def __str__(self):
        return self.username

    @property
    def avatar_path(self):
        if self.avatar and hasattr(self.avatar, 'url'):
            logger.warning(self.avatar.url)
            return self.avatar.url

class SolarSystem(models.Model):

    # An unique numeric id for each SolarSystem
    id = models.AutoField(null=False, primary_key=True)
    # foreign key to the owner
    user = models.ForeignKey(PlanetUser)
    # The name of the SolarSystem
    name = models.CharField(null=False, max_length=50)
    # Description of the SolarSystem
    description = models.CharField(max_length=160)
    # Score of the SolarSystem
    score = models.IntegerField(default = 0)
    # Number of views
    views = models.IntegerField(default=0)
	# Privacy setting of planet. Visibility True - visible to all users
    visibility = models.BooleanField(default = True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.name


class Planet(models.Model):
    # The size of the textures to save (in pixels, should be power-of-two)
    TEXTURE_SIZE = 2048

    # An unique numeric id for each planet
    id = models.AutoField(null=False, primary_key=True)
    # The name of the planet
    name = models.CharField(null=False, max_length=50)
    # foreign key to the owner
    user = models.ForeignKey(PlanetUser)
    # foreign key to the solarsystem it belongs to
    solarSystem = models.ForeignKey(SolarSystem)
    # The planet's texture (as painted by the user).
    texture = models.ImageField(null=False, upload_to='planets')
    # Score of the planet
    score = models.IntegerField(default = 0)
	# Privacy setting of planet. Visibility True - visible to all users
    visibility = models.BooleanField(default = True)

    def save(self, *args, **kwargs):
        # Overridden save() method that resizes the uploaded `texture` if required
        super().save(*args, **kwargs)
        with PIL.Image.open(self.texture.path) as pil_img:
            width, height = pil_img.size
            if width != self.TEXTURE_SIZE or height != self.TEXTURE_SIZE:
                # Rescale image to correct size and save
                logger.debug(f'Planet{self.id}: Image has wrong size {width}x{height},'
                             f'resizing it to {self.TEXTURE_SIZE}x{self.TEXTURE_SIZE}')
                pil_img.resize(
                    (self.TEXTURE_SIZE, self.TEXTURE_SIZE), resample=PIL.Image.BICUBIC)
                pil_img.save(self.texture.path, quality=90, optimize=True)

    def __str__(self) -> str:
        return self.name

class Comment(models.Model):
    # A list of (number, '[' + '*' repeated "number" times + ']' pairs)
    CHOICES = [(n, f'[{"*" * n}]') for n in range(6)]

    planet = models.ForeignKey(Planet)
    user = models.ForeignKey(PlanetUser)
    comment = models.CharField(max_length=200)
    rating = models.IntegerField(choices=CHOICES)

    class Meta:
        # Disallow multiple comments on a planet from the same user
        unique_together = ('planet', 'user')