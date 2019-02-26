from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractUser
from django.contrib.auth.validators import ASCIIUsernameValidator

# Create your models here.*
class MyUserManager(BaseUserManager):
    def create_user(self, username, email, password, picture=None):
        if not email:
            raise ValueError('Users must have an email address')

        if not password:
            raise ValueError('Users must have a password')

        if not username:
            raise ValueError('Users must have a username')

        user = self.model(
            email=self.normalize_email(email),
            username = username,
            avatar = picture,
            password = password,
            identifier = self.make_random_password(40)
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

class PlanetUser(AbstractUser):
    email = models.EmailField(
        verbose_name = 'email address',
        max_length=255)
    identifier = models.CharField(max_length=40, unique=True)
    avatar = models.ImageField(
        upload_to='profile_images', blank=True, null=True)

    username_validator = ASCIIUsernameValidator()

    REQUIRED_FIELDS = ['email']

    objects = MyUserManager()

    def __str__(self):
        return self.username

class Planet(models.Model):
    # An unique numeric id for each planet
    id = models.AutoField(null=False, primary_key=True)
    # The name of the planet
    name = models.CharField(null=False, max_length=50)
    # The planet's texture (as painted by the user).
    texture = models.ImageField(null=False)

    def __str__(self) -> str:
        return self.name
