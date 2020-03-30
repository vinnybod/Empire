import time

from flask import g
from flask.views import MethodView
from flask_smorest import Blueprint
from webargs.flaskparser import abort

from lib.api.handlers import requires_admin
from lib.api.users.schemas import UserSchema, CreateUserInputSchema, DisableUserInputSchema, UpdatePasswordInputSchema, \
    LoginInputSchema, LoginResponseSchema
from lib.common.users import Users
from lib.database import models
from lib.database.base import Session

user_blp = Blueprint(
    'users', 'users', url_prefix='/api/users',
    description='Operations on users'
)


@user_blp.route('/')
class UsersView(MethodView):

    @user_blp.response(UserSchema(exclude=("api_token",), many=True))
    def get(self):
        """
        Returns all users
        """
        return Session().query(models.User).all()

    @requires_admin
    @user_blp.arguments(CreateUserInputSchema)
    @user_blp.response(UserSchema, code=201)
    def post(self, new_data):
        """
        Add a new user
        """
        return Users.add_new_user(new_data['username'], new_data['password'])


@user_blp.route('/<int:user_id>')
class UsersById(MethodView):

    @user_blp.response(UserSchema(exclude=("api_token",)))
    def get(self, user_id):
        """Get user by id"""
        user = Session().query(models.User).filter(models.User.id == user_id).first()

        if user is None:
            abort(404, message='User not found.')

        return user


@user_blp.route('/me')
class UsersMe(MethodView):

    @user_blp.response(UserSchema, code=200)
    def get(self):
        """
        Get logged in user, with apiToken
        """
        return g.user


@user_blp.route('/<int:user_id>/disable')
class UsersDisable(MethodView):

    @requires_admin
    @user_blp.arguments(DisableUserInputSchema)
    @user_blp.response(code=200)
    def put(self, data, user_id):
        if user_id == g.user.id:
            abort(422, message="Cannot disable yourself.")
        if Users.is_admin(user_id):
            abort(422, message="Cannot disable an admin.")

        Users.disable_user(user_id, data['disable'])


@user_blp.route('/<user_id>/password')
class UsersPassword(MethodView):

    @user_blp.arguments(UpdatePasswordInputSchema)
    @user_blp.response(code=200)
    def put(self, data, user_id):
        # Must be an admin or updating self.
        if not (Users.is_admin(g.user.id) or user_id == g.user.id):
            abort(403, message="Not authorized to update this user.")

        Users.update_password(user_id, data['password'])


@user_blp.route('/login')
class UsersLogin(MethodView):

    @user_blp.arguments(LoginInputSchema)
    @user_blp.response(LoginResponseSchema)
    def post(self, data):
        """
        Takes a supplied username and password and returns the current API token
        if authentication is accepted.
        """
        # try to prevent some basic bruting
        time.sleep(2)
        token = Users.user_login(data['username'], data['password'])

        if token:
            return {'token': token}
        else:
            return abort(401, message="Incorrect username or password")


@user_blp.route('/logout')
class UserLogout(MethodView):

    @user_blp.response(code=200)
    def post(self):
        """
        Logs out current user
        """
        Users.user_logout(g.user.id)
