from django.test import TestCase
from planet.models import Planet, PlanetUser, SolarSystem
from django.core.urlresolvers import reverse

class UserTestCase (TestCase):
	def setup(self):
		PlanetUser.objects.create(username='Bob', password='Bob12345678', email='Bob@mail.com')
		PlanetUser.objects.create(username='Anne', password='Anne12345678', email='Anne@mail.com')
		
	def user_account_exists(self):
		Bob = PlanetUser.objects.get(username="Bob")
		self.assertEqual(Bob.username, "Bob")
