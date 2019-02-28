#Agnes

import json
import urllib.parse
import urllib.request
import os

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
	
def run_query(search_terms, size=10):
	#Search terms and number of results to display (default is 10)
	#Search terms have a title, link and summary
	
	webhose_api_key = read_webhose_key()
	
	if not webhose_api_key:
		raise KeyError('Webhose key not found')
		
	#Base url for Webhose API
	root_url = 'http://webhose.io/search'
	
	query_string = urllib.parse.quote(search_terms)
	
	search_url = ('{root_url}?token={key}&format=json&q={query}' '&sort=relevancy&size={size}').format(root_url=root_url, key=webhose_api_key, query=query_string, size=size)
	
	results = []
	
	try:
		#Connect to Webhose API, convert response to python dictionary
		response = urllib.request.urlopen(search_url).read().decode('utf-8')
		json_response = json.loads(response)
		
		#summary restriced to first 200 characters, each result goes in list
		# as a dictionary
		for post in json_response['posts']:
			results.append({'title': post['title'], 'link' : post['url'], 'summary': post['text'][:200]})
			
	except:
		print("Search API query error")
		
	return results
	
