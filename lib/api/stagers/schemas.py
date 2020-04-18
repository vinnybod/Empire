from marshmallow import fields

from lib.api.schemas import CustomOptionSchema, EmpireBaseSchema
from lib.api.validators import validate_listener


class StagerSchema(EmpireBaseSchema):
    author = fields.List(fields.Str(), attribute="Author")
    comments = fields.List(fields.Str(), attribute="Comments")
    description = fields.Str(attribute="Description")
    name = fields.Str(attribute="Name")
    options = fields.Dict(keys=fields.Str(), values=fields.Nested(CustomOptionSchema))


class StagersSchema(EmpireBaseSchema):
    stagers = fields.Nested(StagerSchema, many=True)


class GenerateStagerSchema(EmpireBaseSchema):
    listener = fields.Str(required=True, validate=validate_listener)
    options = fields.Dict(keys=fields.Str(), values=fields.Str(), required=True)


class GenerateStagerResponseSchema(EmpireBaseSchema):
    stager_name = fields.Str()
    options = fields.Dict(keys=fields.Str(), values=fields.Nested(CustomOptionSchema))
    output = fields.Str()
