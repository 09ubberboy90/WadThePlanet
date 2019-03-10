from django.test import TestCase
from planet.models import Planet, PlanetUser, SolarSystem, Comment
from django.core.urlresolvers import reverse
from populate_planet import generate_texture


class DatabaseCreationTestCase (TestCase):
	def setUp(self):
		#Creator object
		PlanetUser.objects.create(username="Bob", password="Bob12345678", email="Bob@mail.com")
		#Rater object
		PlanetUser.objects.create(username="Anne", password="Anne12345678", email="Anne@mail.com")
		Bob = PlanetUser.objects.get(username="Bob")
		Anne = PlanetUser.objects.get(username="Anne")
		
		
		#Create solar system for Bob
		SolarSystem.objects.create(id = 456432, user = Bob, name = "BobsSystem", description = "For random patterns", score = 17)
		BobsSystem = SolarSystem.objects.get(id = 456432)
		
		#Create a test planet
		Planet.objects.create(id = 987, name = "Mars", user = Bob, solarSystem = BobsSystem, texture = generate_texture("bobs_texture"), score = 17)
		
		#Create a comment
		Comment.objects.create(planet = Planet.objects.get(id = 987), user = Anne, comment = "This looks interesting", rating = 4)
		
	def test_user_account_exists(self):
		Bob = PlanetUser.objects.get(username="Bob")
		self.assertEqual(Bob.username, "Bob")
		
	def test_system_exists(self):
		BobsSystem = SolarSystem.objects.get(id = 456432)
		self.assertEqual(BobsSystem.score, 17)
		#Default visibility applied
		self.assertEqual(BobsSystem.visibility, True)
		#Description saved
		self.assertNotEqual(BobsSystem.description, "")
		
	def test_planet_created(self):
		BobsPlanet = Planet.objects.get(id= 987)
		self.assertEqual(BobsPlanet.name, "Mars")
		
	def test_comment_created(self):
		self.assertEqual(Comment.objects.get(user = PlanetUser.objects.get(username="Anne")).rating, 4)
		
	def test_leaderboard(self):
		response = self.client.get(reverse('leaderboard'))
		self.assertEqual(response.status_code, 200)
		#Planet in database reflected in leaderboard
		self.assertContains(response, "Mars")
		
	def test_search(self):
		response = self.client.get("/search/?query=ma")
		self.assertEqual(response.status_code, 200)
		#Search finds Mars for 'ma'
		self.assertContains(response, "Mars")
		#Search does not find user Anne with search query 'ma'
		self.assertNotContains(response, "Anne")
		

		
		
