import threading
import string
import random
import bcrypt
from . import helpers
import json
from pydispatch import dispatcher
from lib.database import base, models


class Users():
    def __init__(self, mainMenu):
        # TODO it looks like the session should be passed in
        self.session = base.session_factory()

        self.mainMenu = mainMenu

        self.conn = self.mainMenu.conn

        self.lock = threading.Lock()

        self.args = self.mainMenu.args

        self.users = {}

    def get_db_connection(self):
        """
        Returns a handle to the DB
        """
        self.mainMenu.conn.row_factory = None
        return self.mainMenu.conn

    def user_exists(self, uid):
        """
        Return whether a user exists or not
        """
        exists = self.session.query(models.User).filter(models.User.id == uid).first()
        if exists:
            return True

        return False

    def add_new_user(self, user_name, password):
        """
        Add new user to cache
        """
        self.session.add(models.User(username=user_name,
                                     password=self.get_hashed_password(password),
                                     last_logon_time=helpers.get_datetime(),
                                     enabled=True,
                                     admin=False))
        self.session.commit()
        signal = json.dumps({
            'print': True,
            'message': "Added {} to Users".format(user_name)
        })
        dispatcher.send(signal, sender="Users")

        return True

    def disable_user(self, uid, disable):
        """
        Disable user
        """
        if not self.user_exists(uid):
            signal = json.dumps({
                'print': True,
                'message': "Cannot disable user that does not exist"
            })
            message = False
        elif self.is_admin(uid):
            signal = json.dumps({
                'print': True,
                'message': "Cannot disable admin account"
            })
            message = False
        else:
            user = self.session.query(models.User).where(models.User.id == uid).first()
            user.enabled = not disable
            self.session.commit()

            signal = json.dumps({
                'print': True,
                'message': 'User {}'.format('disabled' if disable else 'enabled')
            })
            message = True

        dispatcher.send(signal, sender="Users")
        return message

    def user_login(self, user_name, password):
        password_from_db = self.session.query(models.User.password) \
            .filter(models.User.username == user_name) \
            .filter(models.User.enabled is True) \
            .first()

        if password is None:
            return None

        if not self.check_password(password, password_from_db):
            return None

        user = self.session.query(models.User) \
            .filter(models.User.username == user_name) \
            .first()

        user.api_token = self.refresh_api_token()
        user.last_logon_time = helpers.get_datetime()

        self.session.commit()
        # dispatch the event
        signal = json.dumps({
            'print': True,
            'message': "{} connected".format(user_name)
        })
        dispatcher.send(signal, sender="Users")

        return user.api_token

    def get_user_from_token(self, token):
        return self.session.query(models.User).filter(models.User.api_token == token).first()

    def update_username(self, uid, username):
        """
        Update a user's username.
        Currently only when empire is start up with the username arg.
        """
        user = self.session.query(models.User).filter(models.User.id == uid).first()
        user.username = username
        self.session.commit()

        # dispatch the event
        signal = json.dumps({
            'print': True,
            'message': "Username updated"
        })
        dispatcher.send(signal, sender="Users")

        return True

    def update_password(self, uid, password):
        """
        Update the last logon timestamp for a user
        """
        if not self.user_exists(uid):
            return False

        user = self.session.query(models.User).filter(models.User.id == uid).first()
        user.password = self.get_hashed_password(password)
        self.session.commit()

        # dispatch the event
        signal = json.dumps({
            'print': True,
            'message': "Password updated"
        })
        dispatcher.send(signal, sender="Users")

        return True

    def user_logout(self, uid):
        user = self.session.query(models.User).filter(models.User.id == uid).first()
        user.api_token = None
        self.session.commit()

        # dispatch the event
        signal = json.dumps({
            'print': True,
            'message': "User disconnected"
        })
        dispatcher.send(signal, sender="Users")

    def refresh_api_token(self):
        """
        Generates a randomized RESTful API token and updates the value
        in the config stored in the backend database.
        """
        # generate a randomized API token
        rng = random.SystemRandom()
        api_token = ''.join(rng.choice(string.ascii_lowercase + string.digits) for x in range(40))

        return api_token

    def is_admin(self, uid):
        """
        Returns whether a user is an admin or not.
        """
        return self.session.query(models.User.admin).filter(models.User.id == uid).first()

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
