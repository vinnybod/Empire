from marshmallow import Schema, fields
from marshmallow.validate import Length

from lib.api.schemas import EmpireBaseSqlAlchemySchema, EmpireBaseSchema
from lib.database.models import User


class UserSchema(EmpireBaseSqlAlchemySchema):
    class Meta:
        model = User
        include_relationships = True
        load_instance = True
        exclude = ('password',)


class DisableUserInputSchema(EmpireBaseSchema):
    disable = fields.Bool(required=True)


class CreateUserInputSchema(EmpireBaseSchema):
    username = fields.Str(required=True)
    password = fields.Str(required=True, validate=Length(min=5))


class UpdatePasswordInputSchema(EmpireBaseSchema):
    password = fields.Str(required=True, validate=Length(min=5))


class LoginInputSchema(EmpireBaseSchema):
    username = fields.Str(required=True)
    password = fields.Str(required=True)


class LoginResponseSchema(Schema):
    token = fields.Str()
