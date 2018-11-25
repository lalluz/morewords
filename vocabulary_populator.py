from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from morewords import Base, User, Language, Word
#from flask.ext.sqlalchemy import SQLAlchemy


engine = create_engine('sqlite:///morewords.db')

Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)

session = DBSession()

# Add Users
def add_users():
    user_1 = User(username="user_1", email="user_one@mail.com")
    user_1.hash_password("password")
    session.add(user_1)

    user_2 = User(username="user_2", email="user_two@mail.com")
    user_2.hash_password("password")
    session.add(user_2)

    user_3 = User(username="user_3", email="user_three@mail.com")
    user_3.hash_password("password")
    session.add(user_3)

    session.commit()

    return

# Add Languages
def add_languages():
    italian = Language(name="italian", user_id=1)
    session.add(italian)

    spanish = Language(name="spanish", user_id=2)
    session.add(spanish)

    french = Language(name="french", user_id=3)
    session.add(french)

    german = Language(name="german", user_id=1)
    session.add(german)

    session.commit()

    return

# Add Words
def add_words():
    # Add Italian Words
    cane = Word(name="cane", translation="dog", notes="some notes here", is_learned=False, language_id=1, user_id=1)
    session.add(cane)
    gatto = Word(name="gatto", translation="cat", notes="", is_learned=False, language_id=1, user_id=2)
    session.add(gatto)
    mucca = Word(name="mucca", translation="cow", notes="some notes here", is_learned=False, language_id=1, user_id=2)
    session.add(mucca)
    pettirosso = Word(name="pettirosso", translation="robin", notes="", is_learned=False, language_id=1, user_id=1)
    session.add(pettirosso)
    merlo = Word(name="merlo", translation="blackbird", notes="", is_learned=True, language_id=1, user_id=1)
    session.add(merlo)
    gufo = Word(name="gufo", translation="owl", notes="some notes here", is_learned=True, language_id=1, user_id=1)
    session.add(gufo)
    volpe = Word(name="volpe", translation="fox", notes="", is_learned=False, language_id=1, user_id=2)
    session.add(volpe)
    pinguino = Word(name="pinguino", translation="penguin", notes="", is_learned=False, language_id=1, user_id=1)
    session.add(pinguino)
    libro_it = Word(name="libro", translation="book", notes="some notes here", is_learned=False, language_id=1, user_id=1)
    session.add(libro_it)
    casa_it = Word(name="casa", translation="house", notes="", is_learned=True, language_id=1, user_id=1)
    session.add(casa_it)

    # Add Spanish Words
    perro = Word(name="perro", translation="dog", notes="", is_learned=False, language_id=2, user_id=1)
    session.add(perro)
    libro_es = Word(name="libro", translation="book", notes="", is_learned=False, language_id=2, user_id=3)
    session.add(libro_es)
    casa_es = Word(name="casa", translation="house", notes="some notes here", is_learned=True, language_id=2, user_id=2)
    session.add(casa_es)
    mesa = Word(name="mesa", translation="table", notes="", is_learned=True, language_id=2, user_id=2)
    session.add(mesa)
    hola = Word(name="hola", translation="hello", notes="", is_learned=True, language_id=2, user_id=1)
    session.add(hola)
    arroz = Word(name="arroz", translation="rice", notes="", is_learned=False, language_id=2, user_id=3)
    session.add(arroz)
    agua = Word(name="agua", translation="water", notes="some notes here", is_learned=False, language_id=2, user_id=2)
    session.add(agua)
    silla = Word(name="silla", translation="chair", notes="", is_learned=False, language_id=2, user_id=2)
    session.add(silla)

    # Add French Words
    oui = Word(name="oui", translation="yes", notes="some notes here", is_learned=True, language_id=3, user_id=3)
    session.add(oui)
    deux = Word(name="deux", translation="two", notes="", is_learned=False, language_id=3, user_id=3)
    session.add(deux)
    soleil = Word(name="soleil", translation="sun", notes="some notes here", is_learned=True, language_id=3, user_id=3)
    session.add(soleil)
    maison = Word(name="maison", translation="house", notes="", is_learned=True, language_id=3, user_id=3)
    session.add(maison)

    session.commit()

    return

add_users()
add_languages()
add_words()
