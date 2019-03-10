from django.test import TestCase
from planet.models import Planet, PlanetUser, SolarSystem
from django.core.urlresolvers import reverse

class UserTestCase (TestCase):
	def setUp(self):
		PlanetUser.objects.create(username="Bob", password="Bob12345678", email="Bob@mail.com")
		PlanetUser.objects.create(username="Anne", password="Anne12345678", email="Anne@mail.com")
		
		SolarSystem.objects.create(id = 456432, user = PlanetUser.objects.get(username="Bob"), name = "BobsSystem", description = "For random patterns", visibility = True, score = 17)
		
		
		
	def test_user_account_exists(self):
		Bob = PlanetUser.objects.get(username="Bob")
		self.assertEqual(Bob.username, "Bob")
		
	def test_system_exists(self):
		BobsSystem = SolarSystem.objects.get(id = 456432)
		self.assertEqual(BobsSystem.score, 17)
		self.assertNotEqual(BobsSystem.description, "")
		

		
