"""
Connect to the default database at ./data/empire.db.
"""
from __future__ import absolute_import
from __future__ import print_function

import sqlite3
import sys

from lib import arguments
from . import helpers


def connect_to_db():
    try:
        # set the database connectiont to autocommit w/ isolation level
        conn = sqlite3.connect('./data/' + arguments.args.db, check_same_thread=False)
        conn.text_factory = str
        conn.isolation_level = None
        return conn
    except Exception:
        print(helpers.color("[!] Could not connect to database"))
        print(helpers.color("[!] Please run database_setup.py"))
        sys.exit()


db = connect_to_db()
