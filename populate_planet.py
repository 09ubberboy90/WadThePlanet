
#!/usr/bin/env python3

import random
import string
from PIL import Image, ImageDraw


import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "WadThePlanet.settings")

import django
django.setup()
from planet.models import PlanetUser, Planet, SolarSystem,Comment




#Copy the files over to the media destination
#to avoid deleting pictures when deleting database
import shutil
self_path = os.path.abspath(os.path.dirname(__file__))
src = os.path.join(self_path,'_populationmedia/')
dest = os.path.join(self_path,'media/planets/')
src_files = os.listdir(src)
for file_name in src_files:
    full_file_name = os.path.join(src, file_name)
    if (os.path.isfile(full_file_name)):
        shutil.copy(full_file_name, dest)


def populate_old():

    planets1 = [{"name": "planet1",
                 "texture": 'planets/texture1.jpeg'},

                {"name": "planet2",
                 "texture": 'planets/texture2.jpeg'},
                ]

    planets2 = [{"name": "planet3",
                 "texture": 'planets/texture3.jpeg'},

                ]

    planets3 = [{"name": "planet4",
                 "texture": 'planets/texture4.jpeg'},
                ]

    moon = [{"name": "Moon", "texture": 'planets/texture1.jpeg', }
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

    HiddenSystem = [{
                    "name": "hiddenSolarSystem",
                    "description": "Cannot find in search",
                    "planets": moon, }, ]

    users = {"geirtyy": {"solarSys": SolarSystem1},
             "petter": {"solarSys": SolarSystem2},
             "evatyy": {"solarSys": SolarSystem3},
             "crowtyy": {"solarSys": HiddenSystem}, }

    #populate the database
    for user, solarsystems in users.items():
        u = add_user(user)
        for solarsystem in solarsystems["solarSys"]:
            s = add_solarSys(
                u, solarsystem["name"], solarsystem["description"])
            for planet in solarsystem["planets"]:
                add_planet(planet["name"], u, s, planet["texture"])

    create_super_user("superuser")


def populate(number):
    self_dir = os.path.abspath(os.path.dirname(__file__))
    os.makedirs(os.path.join(self_dir, 'media', 'planets'), exist_ok=True)
    print("Generating manual User")
    populate_old()
    counter = 5
    userLs = []
    planetLs = []
    for t in range(number):
        username = "".join(random.choice(string.ascii_lowercase) for i in range(6,15))
        print("Generating Solar systems and planet for user : " + username)
        u = add_user(username)
        userLs.append(u)
        for i in range(random.randint(2,5)):
            SolarSystemName = "SolarSystem"+str(counter)
            SolarSystemDescription = ""
            for j in range(1,16):
                SolarSystemDescription += " " + "".join(random.choice(string.ascii_lowercase) for i in range(random.randint(2,10)))
            s = add_solarSys(u, SolarSystemName, SolarSystemDescription)
            for planet in range(random.randint(2,5)):
                planetName = "planet"+str(counter)
                counter+=1
                planet_object = add_planet(planetName, u, s, generate_texture(planetName),counter%20!=0)
                planetLs.append(planet_object)
    for people in userLs:
        commenting = random.randint(1,10)
        for planet in planetLs:
            if random.randint(0,5) % commenting == 0:
                print(people.username + "is commenting on " + planet.name)
                add_comment(people, planet)

def generate_texture(name):
    img = Image.new('RGB', (2048, 2048), (
        random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))
    draw = ImageDraw.Draw(img)
    draw.rectangle((random.randint(0, 2048), random.randint(0, 2048), random.randint(
        0, 2048), random.randint(0, 2048)), fill=(
        random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))
    draw.pieslice((random.randint(0, 2048), random.randint(0, 2048), random.randint(
        0, 2048), random.randint(0, 2048)), random.randint(0, 360), random.randint(0, 360), fill=(
        random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))
    draw.ellipse((random.randint(0, 2048), random.randint(0, 2048), random.randint(
        0, 2048), random.randint(0, 2048)), fill=(
        random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))
    pos = []
    for i in range(random.randint(3,10)):
        pos.append((random.randint(0, 2048), random.randint(0, 2048)))
    draw.polygon(pos, fill=(
        random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))

    rel_path = 'planets/'+name+'.png'
    abs_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'media', rel_path)
    if os.path.exists(abs_path):
        os.unlink(abs_path)
    img.save(abs_path,'JPEG')
    return rel_path  # Otherwise weird things may happen


#helper functions
def add_user(username):
    email = str(username + "@hotmail.com")
    password = "".join(random.choice(string.ascii_lowercase) for i in range(10))
    user = PlanetUser.objects.get_or_create(username=username, password=password,email=email)[0]
    user.save()
    return user


def add_planet(name, user, solarSys, texture, visibility=True):
    planet = Planet.objects.get_or_create(name=name, user=user,solarSystem=solarSys,texture=texture)[0]
    planet.visibility = visibility
    planet.save()
    return planet


def add_solarSys(user, name, description='', score=0):
    solarSys = SolarSystem.objects.get_or_create(user=user, name=name)[0]
    solarSys.description = description
    solarSys.score = score
    solarSys.save()
    return solarSys

def add_comment(user,planet):
    comment = Comment.objects.create(user=user,planet=planet,comment="abc",rating=1)
    comment.comment = "".join(random.choice(
        string.ascii_lowercase) for i in range(10))
    comment.rating = random.randint(1,5)
    comment.save()
    return comment

def create_super_user(username):
    email = str(username + "@hotmail.com")
    u = PlanetUser.objects.create_superuser(username=username, email=email, password="superuser")


#start execution here

if __name__ == '__main__':
    populate(5)
