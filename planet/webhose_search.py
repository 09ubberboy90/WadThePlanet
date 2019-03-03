import os
import django
from planet.models import Planet, SolarSystem, PlanetUser

#Don;t need this
import json
import urllib.parse
import urllib.request

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "planet.settings")
django.setup()


def query(search_terms, results=10):

#	print(all_planets, all_systems, all_users)
	print(all_planets)
	return search_terms
	
	
def run_query(search_terms, results=10):

	all_planets = Planet.objects.all()
	all_systems = SolarSystem.objects.all()
	all_users = PlanetUser.objects.all()

	results = []
	
	all_planets = all_planets.exclude(visibility=False).filter(name__contains=search_terms)
	all_systems = all_systems.exclude(visibility=False).filter(name__contains=search_terms)
	all_users = all_users.exclude(username="admin").filter(username__contains=search_terms)
	
	for planet in all_planets:
		
		results.append(planet)
		
	for system in all_systems:
		
		results.append(system)
		
	for user in all_users:
		
		results.append(user)
		
	return (results)