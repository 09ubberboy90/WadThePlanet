import random
import string

import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "WadThePlanet.settings")

import django
django.setup()
from planet.models import PlanetUser, Planet, SolarSystem
self_path = os.path.abspath(os.path.dirname(__file__))

def populate():





    planets1 = [ {"name": "planet1",
                  "texture": os.path.join(self_path,'media/_population_pictures/texture1.jpeg')},

                {"name": "planet2",
                 "texture": os.path.join(self_path,'media/_population_pictures/texture2.jpeg')},
    ]

    planets2 = [{"name": "planet3",
                 "texture": os.path.join(self_path,'media/_population_pictures/texture3.jpeg')},

    ]

    planets3 = [{"name": "planet4",
                 "texture": os.path.join(self_path,'media/_population_pictures/texture4.jpeg')},
    ]



    SolarSystem1 = [{
                    "name": "FirstSolarSystem",
                    "description": "Cool solarsys",
                    "planets": planets1,
                    },
    ]

    SolarSystem2 = [{
                    "name": "SecondSolarSystem",
                    "description": "Cooler solarsys",
                    "planets": planets2,
                    },
    ]

    SolarSystem3 = [{
                    "name": "ThirdSolarSystem",
                    "description": "Coolest solarsys",
                    "planets": planets3,
                    },
    ]

    users = {"geir": {"solarSys": SolarSystem1},
             "petter": {"solarSys": SolarSystem2},
             "eva": {"solarSys": SolarSystem3},}



    for user, solarsystems in users.items():
        u = add_user(user)
        for solarsystem in solarsystems["solarSys"]:
            s = add_solarSys(u, solarsystem["name"], solarsystem["description"])
            for planet in solarsystem["planets"]:
                add_planet(planet["name"], u, s, planet["texture"])




def add_user(username):
    email = str(username + "@hotmail.com")
    password = "".join(random.choice(string.ascii_lowercase) for i in range(10))
    user = PlanetUser.objects.get_or_create(username=username, password=password,email=email)[0]
    user.save()
    return user


def add_planet(name, user, solarSys, texture, score=0):
    planet = Planet.objects.get_or_create(name=name, user=user,solarSystem=solarSys,texture=texture)[0]
    planet.score = score
    planet.save()
    return planet


def add_solarSys(user, name, description='', score=0, views=0):
    solarSys = SolarSystem.objects.get_or_create(user=user, name=name)[0]
    solarSys.description = description
    solarSys.score = score
    solarSys.views = views
    solarSys.save()
    return solarSys


#start execution here
if __name__ == '__main__':
    print("Starting Rango population script...")
    populate()
