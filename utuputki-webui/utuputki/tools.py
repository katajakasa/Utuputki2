# -*- coding: utf-8 -*-

import settings
import sys
import getpass
from passlib.hash import pbkdf2_sha256
from db import USERLEVELS, db_init, db_session, User
from sqlalchemy.exc import IntegrityError


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

print("Utuputki utilities")
print("create_admin - Creates a new admin user")
print("create_test_admin - Create a test admin user")
exit(0)
