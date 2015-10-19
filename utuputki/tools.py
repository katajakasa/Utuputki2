# -*- coding: utf-8 -*-


import sys
import getpass
from passlib.hash import pbkdf2_sha256
from sqlalchemy.exc import IntegrityError

import settings
from common.db import USERLEVELS, db_init, db_session, User, Event, Player
from common.utils import generate_session


def create_admin(_username, _password):
    settings.config_init()
    db_init(settings.DATABASE_CONFIG)
    pw_hash = pbkdf2_sha256.encrypt(_password)
    s = db_session()
    user = User(username=_username,
                nickname=_username,
                email="admin@admin.inv",
                password=pw_hash,
                level=USERLEVELS['admin'])
    s.add(user)
    try:
        s.commit()
        print("User '{}' created.".format(_username))
    except IntegrityError:
        print("User {} already exists.".format(_username))
    finally:
        s.close()

if 'create_admin' in sys.argv:
    username = raw_input("Username: ")
    password = getpass.getpass()
    create_admin(username, password)
    exit(0)

if 'create_test_admin' in sys.argv:
    create_admin('admin', 'admin')
    exit(0)

if 'create_event' in sys.argv:
    settings.config_init()
    db_init(settings.DATABASE_CONFIG)
    name = raw_input("Event name: ")

    s = db_session()
    event = Event(name=name, visible=True)
    s.add(event)
    s.commit()
    s.close()
    exit(0)

if 'list_events' in sys.argv:
    settings.config_init()
    db_init(settings.DATABASE_CONFIG)
    s = db_session()
    print("ID  Name")
    for event in s.query(Event).all():
        print("{:3} {}".format(event.id, event.name))
    s.close()
    exit(0)

if 'create_player' in sys.argv:
    settings.config_init()
    db_init(settings.DATABASE_CONFIG)
    event_id = int(raw_input("Event ID: "))
    name = raw_input("Player name: ")

    s = db_session()
    player = Player(event=event_id, name=name, token=generate_session()[:16])
    s.add(player)
    s.commit()
    s.close()
    exit(0)

if 'list_players' in sys.argv:
    settings.config_init()
    db_init(settings.DATABASE_CONFIG)
    s = db_session()
    print("Id  Ev  Name             Token")
    for player in s.query(Player).all():
        print("{:3} {:3} {:16} {}".format(player.id, player.event, player.name, player.token))
    s.close()
    exit(0)

print("Utuputki utilities")
print("create_admin - Creates a new admin user")
print("create_test_admin - Create a test admin user")
print("create_event - Create an event")
print("list_events - List all events")
print("create_player - Create a player for event")
print("list_players - List all players")
exit(0)
