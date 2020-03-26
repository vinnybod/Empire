from flask import g
from flask import jsonify
from flask.views import MethodView
from flask_smorest import Blueprint
from webargs.flaskparser import abort

from lib.api.users.schemas import UserSchema, CreateUserInputSchema, DisableUserInputSchema, UpdatePasswordInputSchema
from lib.common.users import Users
from lib.database import models
from lib.database.base import Session

user_blp = Blueprint(
    'users', 'users', url_prefix='/api/users',
    description='Operations on users'
)

# Todo standardized exception handling
@user_blp.route('/')
class UsersView(MethodView):

    # todo exclude password on the schema itself
    @user_blp.response(UserSchema(exclude=("password", "api_token"), many=True))
    def get(self):
        """
        Returns all users
        """
        return Session().query(models.User).all()

    @user_blp.arguments(CreateUserInputSchema)
    @user_blp.response(UserSchema, code=201)
    def post(self, new_data):
        """
        Add a new user
        """
        # Check if user is an admin
        if not Users.is_admin(g.user.id):
            abort(403)

        return Users.add_new_user(new_data['username'], new_data['password'])


@user_blp.route('/<int:user_id>')
class UsersById(MethodView):

    @user_blp.response(UserSchema(exclude=("password", "api_token")))
    def get(self, user_id):
        """Get user by id"""
        user = Session().query(models.User).filter(models.User.id == user_id).first()

        # todo here is where i've seen it deferred to a dao and catches a NotFoundException from the dao
        if user is None:
            abort(404, message='User not found.')

        return user


@user_blp.route('/me')
class UsersMe(MethodView):

    @user_blp.response(UserSchema(exclude=("password",)), code=200)
    def get(self):
        """
        Get logged in user, with apiToken
        """
        return g.user

# Todo can we validate int in the path
# TODO is the input schema auto validated
@user_blp.route('/<int:user_id>/disable')
class UsersDisable(MethodView):

    @user_blp.arguments(DisableUserInputSchema)
    @user_blp.response(UserSchema(exclude=("password",)), code=200)
    def put(self, data, user_id):
        # Don't disable yourself
        if user_id == g.user.id:
            # todo abort?
            return jsonify({'errors': ['Cannot disable yourself']}, 400)

        # todo add admin check as an annotation
        # User performing the action should be an admin.
        # User being updated should not be an admin.
        if not Users.is_admin(g.user.id) or Users.is_admin(user_id):
            abort(403)

        status = Users.disable_user(user_id, data['disable'])

        # todo return object itself? 201? 204?
        return jsonify({'success': status})


@user_blp.route('/<user_id>/password')
class UsersPassword(MethodView):

    @user_blp.arguments(UpdatePasswordInputSchema)
    @user_blp.response(UserSchema(exclude=("password",)), code=200)
    def put(self, data, user_id):
        # Must be an admin or updating self.
        if not (Users.is_admin(g.user.id) or user_id == g.user.id):
            abort(403)

        status = Users.update_password(user_id, data['password'])

        # return 201 ? 204? 200 with no body?
        return jsonify({'success': status})
