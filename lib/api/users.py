from flask import g
from flask import jsonify
from flask.views import MethodView
from flask_smorest import Blueprint
from webargs.flaskparser import abort

from lib.api.input import CreateUserInputSchema
from lib.common.users import Users
from lib.database import models
from lib.database.base import Session
from lib.database.models import UserSchema

user_blp = Blueprint(
    'users', 'users', url_prefix='/users',
    description='Operations on users'
)


@user_blp.route('/')
class UsersView(MethodView):

    @user_blp.response(UserSchema(exclude=("password", "api_token"), many=True))
    def get(self):
        """
        Returns all users
        """
        users = Session().query(models.User).all()

        return users

    @user_blp.arguments(CreateUserInputSchema)
    @user_blp.response(UserSchema, code=201)
    def post(self, new_data):
        """
        Add a new user
        """
        # Check if user is an admin
        if not Users.is_admin(g.user.id):
            abort(403)

        status = Users.add_new_user(new_data.username, new_data.password)
        return jsonify({'success': status})


@user_blp.route('/<user_id>')
class UsersById(MethodView):

    @user_blp.response(UserSchema)
    def get(self, user_id):
        """Get user by id"""
        try:
            item = Session().query(models.User).filter(models.User.id == user_id).first()
        except Exception:
            abort(404, message='Item not found.')
        return item


@user_blp.route('/me')
class UsersMe(MethodView):

    @user_blp.response(UserSchema(exclude=("password",)), code=200)
    def get(self):
        """
        Get logged in user, with apiToken
        """
        return g.user
