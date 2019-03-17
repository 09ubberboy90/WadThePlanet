import os
import django
from planet.models import Planet, SolarSystem, PlanetUser
from typing import Iterable, Tuple

def run_query(search_terms: Iterable[str], count: int = 100) -> Tuple:
    # Find planets that are visible and contain search term in their name
    found_planets = Planet.objects.all().exclude(
        visibility=False).filter(name__contains=search_terms)
    # Find solar systems that with search term in the name
    found_systems = SolarSystem.objects.all().exclude(
        visibility=False).filter(name__contains=search_terms)
    # Find search term in solar system description
    system_descriptions = SolarSystem.objects.all().exclude(
        visibility=False).filter(description__contains=search_terms)

    # Find matching user names, except super user
    found_users = PlanetUser.objects.all().exclude(
        username="superuser").filter(username__contains=search_terms)

    # Combine solar systems name and description and remove duplicates
    found_systems.union(system_descriptions).distinct()
    return found_planets, found_systems, found_users
