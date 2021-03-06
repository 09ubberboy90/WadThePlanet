import logging
import os
import PIL
from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager
from django.contrib.auth.validators import ASCIIUsernameValidator
from WadThePlanet import settings
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
import re
from django.core.exceptions import ValidationError
from django.dispatch import receiver


# ======================== Utilities ===========================================

logger = logging.getLogger(__name__)

DISALLOWED_NAMES = ['admin', 'about', 'contact', 'login',
                    'logout', 'register', 'search', 'leaderboard']
'''Disallowed user names; may conflict with system pages.'''


def name_validator(name: str):
    '''A Django validator for valid user/system/planet names'''
    must_not_match = '(?!' + '|'.join(DISALLOWED_NAMES) + ')'
    must_match = r'([A-Za-z0-9]+)'
    if not re.match(f'^{must_not_match}{must_match}$', name):
        raise ValidationError(
            'Names should be alphanumeric, excluding some reserved words')


def content_file_name(instance, filename):
    ext = filename.split('.')[-1]
    filename = f'{instance.username}.{ext}'
    return os.path.join('profile_images/', filename)

# ======================== Models ==============================================


class PlanetUser(AbstractUser):
    email = models.EmailField(
        verbose_name='email address',
        max_length=255)
    avatar = models.ImageField(
        upload_to=content_file_name, blank=True, null=True)

    REQUIRED_FIELDS = ['email']
    username_validator = name_validator

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
    user = models.ForeignKey(PlanetUser, on_delete=models.CASCADE)
    # The name of the SolarSystem
    name = models.CharField(null=False, max_length=50,
                            validators=[name_validator])
    # Description of the SolarSystem
    description = models.CharField(max_length=160)
    # Privacy setting of planet. Visibility True - visible to all users
    visibility = models.BooleanField(blank=False, default=True)
    # Score of the SolarSystem
    score = models.IntegerField(default=0)

    class Meta:
        # Disallow multiple solar systems with the same name from the same user
        unique_together = ('user', 'name')

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
    name = models.CharField(null=False, max_length=50,
                            validators=[name_validator])
    # foreign key to the owner
    user = models.ForeignKey(PlanetUser, on_delete=models.CASCADE)
    # foreign key to the solarsystem it belongs to
    solarSystem = models.ForeignKey(SolarSystem, on_delete=models.CASCADE)
    # The planet's texture (as painted by the user).
    texture = models.ImageField(null=False, upload_to='planets')
    # Privacy setting of planet. Visibility True - visible to all users
    visibility = models.BooleanField(blank=False, default=True)
    # Score of the planet
    score = models.IntegerField(default=0)

    class Meta:
        # Disallow multiple planets with the same name in the same solar system
        unique_together = ('solarSystem', 'name')

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

    def delete(self, *args, **kwargs):
        self.solarSystem.score -= self.score
        self.solarSystem.save()
        super().delete(*args, **kwargs)

    def __str__(self) -> str:
        return self.name


class Comment(models.Model):
    # A list of (number, choice to show to the user) pair for ratings
    CHOICES = [(0, 'No rating')] + \
        [(n, f'{"🟊" * n}{"☆" * (5 - n)}') for n in range(1, 6)]

    planet = models.ForeignKey(Planet, on_delete=models.CASCADE)
    user = models.ForeignKey(PlanetUser, on_delete=models.CASCADE)
    comment = models.CharField(max_length=200, null=False)
    rating = models.IntegerField(choices=CHOICES, null=False)

    class Meta:
        # Disallow multiple comments on a planet from the same user
        unique_together = ('planet', 'user')

    def save(self, *args, **kwargs):
        '''
        Save the comment, recalculating the score of the parent planet and solar
        system as needed.
        '''
        try:
            # Get the comment with our same primary key; it will be the previous
            # version of this comment, containing the previous rating
            prev_comment = Comment.objects.get(pk=self.pk)
            prev_rating = prev_comment.rating
        except Comment.DoesNotExist:
            # There was no previous comment; assume a previous value of 0 = no rating
            prev_rating = 0

        #Add comment score to planet score
        self.planet.score += self.rating - prev_rating
        self.planet.save()

        #Add comment score to solar system score
        self.planet.solarSystem.score += self.rating - prev_rating
        self.planet.solarSystem.save()

        # Apply the changes to the DB row
        super().save(*args, **kwargs)
        return self

    def delete(self, *args, **kwargs):
        self.planet.score -= self.score
        self.planet.save()
        self.planet.solarSystem.score -= self.score
        self.planet.solarSystem.save()
        super().delete(*args, **kwargs)
