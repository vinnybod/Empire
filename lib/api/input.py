from marshmallow import Schema, fields
from marshmallow.validate import Length, Range


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
