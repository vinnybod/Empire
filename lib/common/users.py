import string
import random
import bcrypt
from . import helpers
import json
from pydispatch import dispatcher
from lib.database import models
from lib.database.base import Session


class Users:

    @staticmethod
    def user_exists(uid):
        """
        Return whether a user exists or not
        """
        exists = Session().query(models.User).filter(models.User.id == uid).first()
        if exists:
            return True

        return False

    @staticmethod
    def add_new_user(user_name, password):
        """
        Add new user to cache
        """
        user = models.User(username=user_name,
                           password=Users.get_hashed_password(password),
                           last_logon_time=helpers.get_datetime(),
                           enabled=True,
                           admin=False)
        Session().add()
        Session().commit()

        signal = json.dumps({
            'print': True,
            'message': "Added {} to Users".format(user_name)
        })
        dispatcher.send(signal, sender="Users")

        return user

    @staticmethod
    def disable_user(uid, disable):
        """
        Disable user
        """
        if not Users.user_exists(uid):
            signal = json.dumps({
                'print': True,
                'message': "Cannot disable user that does not exist"
            })
            message = False
        elif Users.is_admin(uid):
            signal = json.dumps({
                'print': True,
                'message': "Cannot disable admin account"
            })
            message = False
        else:
            user = Session().query(models.User).where(models.User.id == uid).first()
            user.enabled = not disable
            Session().commit()

            signal = json.dumps({
                'print': True,
                'message': 'User {}'.format('disabled' if disable else 'enabled')
            })
            message = True

        dispatcher.send(signal, sender="Users")
        return message

    @staticmethod
    def user_login(user_name, password):
        print("sup boiiii")
        password_from_db = Session().query(models.User.password) \
            .filter(models.User.username == user_name) \
            .filter(models.User.enabled == True) \
            .first()

        if password_from_db is None:
            return None

        if not Users.check_password(password, password_from_db.password):
            return None

        user = Session().query(models.User) \
            .filter(models.User.username == user_name) \
            .first()

        user.api_token = Users.refresh_api_token()
        user.last_logon_time = helpers.get_datetime()

        Session().commit()
        # dispatch the event
        signal = json.dumps({
            'print': True,
            'message': "{} connected".format(user_name)
        })
        dispatcher.send(signal, sender="Users")

        return user.api_token

    @staticmethod
    def get_user_from_token(token):
        return Session().query(models.User).filter(models.User.api_token == token).first()

    @staticmethod
    def update_username(uid, username):
        """
        Update a user's username.
        Currently only when empire is start up with the username arg.
        """
        user = Session().query(models.User).filter(models.User.id == uid).first()
        user.username = username
        Session().commit()

        # dispatch the event
        signal = json.dumps({
            'print': True,
            'message': "Username updated"
        })
        dispatcher.send(signal, sender="Users")

        return True

    @staticmethod
    def update_password(uid, password):
        """
        Update the last logon timestamp for a user
        """
        if not Users.user_exists(uid):
            return False

        user = Session().query(models.User).filter(models.User.id == uid).first()
        user.password = Users.get_hashed_password(password)
        Session().commit()

        # dispatch the event
        signal = json.dumps({
            'print': True,
            'message': "Password updated"
        })
        dispatcher.send(signal, sender="Users")

        return True

    @staticmethod
    def user_logout(uid):
        user = Session().query(models.User).filter(models.User.id == uid).first()
        user.api_token = None
        Session().commit()

        # dispatch the event
        signal = json.dumps({
            'print': True,
            'message': "User disconnected"
        })
        dispatcher.send(signal, sender="Users")

    @staticmethod
    def refresh_api_token():
        """
        Generates a randomized RESTful API token and updates the value
        in the config stored in the backend database.
        """
        # generate a randomized API token
        rng = random.SystemRandom()
        api_token = ''.join(rng.choice(string.ascii_lowercase + string.digits) for x in range(40))

        return api_token

    @staticmethod
    def is_admin(uid):
        """
        Returns whether a user is an admin or not.
        """
        return Session().query(models.User.admin).filter(models.User.id == uid).first()

    @staticmethod
    def get_hashed_password(plain_text_password):
        if isinstance(plain_text_password, str):
            plain_text_password = plain_text_password.encode('UTF-8')

        return bcrypt.hashpw(plain_text_password, bcrypt.gensalt())

    @staticmethod
    def check_password(plain_text_password, hashed_password):
        if isinstance(plain_text_password, str):
            plain_text_password = plain_text_password.encode('UTF-8')
        if isinstance(hashed_password, str):
            hashed_password = hashed_password.encode('UTF-8')

        return bcrypt.checkpw(plain_text_password, hashed_password)
