import random
import string

import bcrypt

from lib.database import models


def get_default_user():
    return models.User(username="empireadmin",
                       password=bcrypt.hashpw(b"password123", bcrypt.gensalt()),
                       enabled=True,
                       admin=True)


def get_default_config():
    return models.Config(staging_key="",
                         install_path="",
                         ip_whitelist="",
                         ip_blacklist="",
                         autorun_command="",
                         autorun_data="",
                         rootuser=True,
                         obfuscate=0,
                         obfuscate_command=r"Token\All\1")


def get_default_functions():
    return models.Function(
        Invoke_Empire=''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(5)),
        Invoke_Mimikatz=''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(5)))