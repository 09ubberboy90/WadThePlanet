import os
import django
from planet.models import Planet

#Don;t need this
import json
import urllib.parse
import urllib.request

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "planet.settings")
django.setup()

all_planets = Planet.objects.all
#all_systems = SolarSystem.objects.all
#all_users = PlanetUser.objects.all

def run_query(search_terms, results=10):

#	print(all_planets, all_systems, all_users)
	print("search placeholder")
	return

def read_webhose_key():
	# Search API key comes for search.key file
	wehose_api_key = None
	
	keyFile = 'search.key' #API key is here
	
	if not os.path.isfile('search.key'):
		keyFile = '../search.key' #This allows to run search outside planet app form inside planet folder.
	
	try:
		with open ('search.key', 'r') as f:
			webhose_api_key = f.readline().strip()
	
	except:
		raise IOError('search.key file not found')
	
	return webhose_api_key
	
