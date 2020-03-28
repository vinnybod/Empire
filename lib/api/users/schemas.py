from marshmallow import Schema, fields
from marshmallow.validate import Length

from lib.api.schemas import CamelCaseSqlAlchemyAutoSchema
from lib.database.models import User


class UserSchema(CamelCaseSqlAlchemyAutoSchema):
    class Meta:
        model = User
        include_relationships = True
        load_instance = True
        exclude = ('password',)


class DisableUserInputSchema(Schema):
    disable = fields.Bool(required=True)


class CreateUserInputSchema(Schema):
    username = fields.Str(required=True)
    password = fields.Str(required=True, validate=Length(min=5))


class UpdatePasswordInputSchema(Schema):
    password = fields.Str(required=True, validate=Length(min=5))


class LoginInputSchema(Schema):
    username = fields.Str(required=True)
    password = fields.Str(required=True)


class LoginResponseSchema(Schema):
    token = fields.Str()
