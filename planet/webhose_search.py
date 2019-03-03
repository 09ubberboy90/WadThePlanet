import os
import django
from planet.models import Planet, SolarSystem, PlanetUser

#Don;t need this
import json
import urllib.parse
import urllib.request

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "planet.settings")
django.setup()
	
def run_query(search_terms, count):

	#Find planets that are visible and contain search term in their name
	found_planets = Planet.objects.all().exclude(visibility=False).filter(name__contains=search_terms)
	#Find solar systems that with search term in the name
	found_systems = SolarSystem.objects.all().exclude(visibility=False).filter(name__contains=search_terms)
	#Find search term in solar system description
	system_descriptions= SolarSystem.objects.all().exclude(visibility=False).filter(description__contains=search_terms)

	#Find matching user names, except super user
	found_users = PlanetUser.objects.all().exclude(username="superuser").filter(username__contains=search_terms)
	
	#Combine solar systems name and description and remove duplicates
	found_systems.union(system_descriptions).distinct()

	results = []
	
	
	for item in found_planets:
		results.append(item)
		
	for item in found_systems:
		results.append(item)
		
	for item in found_users:
		results.append(item)
		
	if len(results) > count:
		results = results[0:count]
		
	return (results)