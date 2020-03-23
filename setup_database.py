#!/usr/bin/env python3

from __future__ import print_function

import hashlib
import os
import random
import string
from builtins import input

import bcrypt

from lib.database import models
from lib.database.base import Session

###################################################
#
# Default values for the config
#
###################################################

# Staging Key is set up via environmental variable
# or via command line. By setting RANDOM a randomly
# selected password will automatically be selected
# or it can be set to any bash acceptable character
# set for a password.

STAGING_KEY = os.getenv('STAGING_KEY', "BLANK")
punctuation = '!#%&()*+,-./:;<=>?@[]^_{|}~'

# otherwise prompt the user for a set value to hash for the negotiation password
if STAGING_KEY == "BLANK":
    choice = input("\n [>] Enter server negotiation password, enter for random generation: ")
    if choice == "":
        # if no password is entered, generation something random
        STAGING_KEY = ''.join(random.sample(string.ascii_letters + string.digits + punctuation, 32))
    else:
        STAGING_KEY = hashlib.md5(choice.encode('utf-8')).hexdigest()
elif STAGING_KEY == "RANDOM":
    STAGING_KEY = ''.join(random.sample(string.ascii_letters + string.digits + punctuation, 32))

# Calculate the install path. We know the project directory will always be the parent of the current directory. Any modifications of the folder structure will
# need to be applied here.
INSTALL_PATH = os.path.dirname(os.path.dirname(os.path.realpath(__file__))) + "/"

# an IP white list to ONLY accept clients from
#   format is "192.168.1.1,192.168.1.10-192.168.1.100,10.0.0.0/8"
IP_WHITELIST = ""

# an IP black list to reject accept clients from
#   format is "192.168.1.1,192.168.1.10-192.168.1.100,10.0.0.0/8"
IP_BLACKLIST = ""

OBFUSCATE = 0

OBFUSCATE_COMMAND = r'Token\All\1'

API_USERNAME = "empireadmin"

API_PASSWORD = bcrypt.hashpw(b"password123", bcrypt.gensalt())

config = Session().query(models.Config).first()
config.staging_key = STAGING_KEY
config.install_path = INSTALL_PATH
config.ip_blacklist = IP_BLACKLIST
config.ip_whitelist = IP_WHITELIST
config.obfuscate = OBFUSCATE
config.obfuscate_command = OBFUSCATE_COMMAND

user = Session.query(models.User).first()
user.username = API_USERNAME
user.password = API_PASSWORD

Session.commit()

print("\n [*] Database setup completed!\n")
