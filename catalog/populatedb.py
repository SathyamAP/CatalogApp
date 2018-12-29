#!/usr/bin/env python

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session

from model import Category, Item, User

engine = create_engine('sqlite:///categoryapp.db')
Base = declarative_base()
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine, autocommit=False)
session = scoped_session(DBSession)

# cleanup db if there are rows present
print("cleaning up db")
rows = session.query(Item).delete()
print(str(rows) + " items deleted")
rows = session.query(Category).delete()
print(str(rows) + " categories deleted")
rows = session.query(User).delete()
print(str(rows) + " users deleted")
session.commit()

print ("starting to populate data....")

# create a new dummy user
user = User(name="Kiran K", email="kiran.k@gmail.com")
session.add(user)
user2 = User(name="Maya S", email="maya.s@gmail.com")
session.add(user)
session.commit()

# create categories
cat_comics = Category(name="Comics")
session.add(cat_comics)

cat_fiction = Category(name="Fiction")
session.add(cat_fiction)

cat_fantacy = Category(name="Fantacy")
session.add(cat_fantacy)

cat_horror = Category(name="Horror")
session.add(cat_horror)

cat_mystery = Category(name="Mystery")
session.add(cat_mystery)

cat_misc = Category(name="Miscellaneous")
session.add(cat_misc)

cat_tech = Category(name="Technical")
session.add(cat_tech)

# create items under categories
item_tintin = Item(name="The Adventures of Tintin", category=cat_comics,
                   created_user=user,
                   description="""The Adventures of Tintin
        is a series of 24 comic albums created by Belgian cartoonist Georges
        Remi, who wrote under the pen name Herge. The series was one of the
        most popular European comics of the 20th century. By 2007, a century
        after Herge's birth in 1907,[1] Tintin had been published in more
        than 70 languages with sales of more than 200 million copies, and had
        been adapted for radio, television, theatre, and film.""")
item_calvin = Item(name="Calvin and Hobbes", category=cat_comics,
                   created_user=user2,
                   description="""Calvin and Hobbes is a daily comic
    strip by American cartoonist Bill Watterson that was syndicated from
    November 18, 1985 to December 31, 1995. Commonly cited as "the last great
    newspaper comic",[2][3][4] Calvin and Hobbes has enjoyed broad and enduring
    popularity, influence, and academic interest.""")
item_archie = Item(name="Archie", category=cat_comics,
                   created_user=user,
                   description="""Archie (also known as Archie Comics) is
    an ongoing comic book series featuring the Archie Comics character Archie
    Andrews. The character first appeared in Pep Comics #22 (cover dated
    December 1941). Archie proved to be popular enough to warrant his own
    self-titled ongoing comic book series which began publication in the winter
    of 1942 and ran until June 2015. A second series began publication in
    July 2015, featuring a reboot of the Archie universe with a new character
    design aesthetic and a more mature story format and scripting, aimed for
    older, contemporary teenage and young adult readers. The printed comic
    book format is different from the previous publications.""")

session.add(item_tintin)
session.add(item_calvin)
session.add(item_archie)

item_harry_potter = Item(name="Harry Potter",
                         category=cat_fantacy, created_user=user2,
                         description="""Harry Potter is a series of fantasy
    novels written by British author J. K. Rowling. The novels chronicle the
    lives of a young wizard, Harry Potter, and his friends Hermione Granger and
    Ron Weasley, all of whom are students at Hogwarts School of Witchcraft and
    Wizardry. The main story arc concerns Harry's struggle against Lord
    Voldemort, a dark wizard who intends to become immortal, overthrow the
    wizard governing body known as the Ministry of Magic, and subjugate all
    wizards and Muggles (non-magical people).""")
item_lord_rings = Item(name="The Lord of the Rings", category=cat_fantacy,
                       created_user=user,
                       description="""The Lord of the Rings is an epic
    high fantasy novel written by English author and scholar J. R. R. Tolkien.
    The story began as a sequel to Tolkien's 1937 fantasy novel The Hobbit,
    but eventually developed into a much larger work. Written in stages
    between 1937 and 1949, The Lord of the Rings is one of the best-selling
    novels ever written, with over 150 million copies sold. """)

session.add(item_harry_potter)
session.add(item_lord_rings)

item_infernal_devices = Item(name="The Infernal devices",
                             category=cat_fiction, created_user=user,
                             description="""Infernal Devices is a steampunk
    novel by K.W.Jeter, published in 1987. The novel was republished in 2011 by
    Angry Robot Books with a new introduction by the author, cover art by
    John Coulthart, and an afterword by Jeff VanderMeer. """)

session.add(item_infernal_devices)

item_hercule1 = Item(name="The Murder on the Orient Express",
                     category=cat_mystery, created_user=user,
                     description="""Murder on the
    Orient Express is a detective novel by British writer Agatha Christie
    featuring the Belgian detective Hercule Poirot. It was first published in
    the United Kingdom by the Collins Crime Club on 1 January 1934. In the
    United States, it was published on 28 February 1934, under the title of
    Murder in the Calais Coach, by Dodd, Mead and Company. """)

item_hercule2 = Item(name="And Then There Were None", category=cat_mystery,
                     created_user=user2,
                     description="""And Then There Were None is a mystery
    novel by English writer Agatha Christie, her best selling novel and
    described by her as the most difficult of her books to write.[2] It was
    first published in the United Kingdom by the Collins Crime Club on 6
    November 1939, as Ten Little Niggers,[3] after the British blackface song,
    which serves as a major plot point """)

session.add(item_hercule1)
session.add(item_hercule2)
session.commit()

print("Users added in db : " + str(len(session.query(User).all())))
print("Categories added in db : " + str(len(session.query(Category).all())))
print("Items added in db : " + str(len(session.query(Item).all())))

print ("Finished populating data")
