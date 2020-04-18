from marshmallow import Schema, fields
from marshmallow.validate import Length

from lib.api.schemas import CustomOptionSchema
from lib.api.validators import validate_agent


class ModuleSchema(Schema):
    author = fields.List(fields.Str(), attribute="Author")
    comments = fields.List(fields.Str(), attribute="Comments")
    description = fields.Str(attribute="Description")
    name = fields.Str(attribute="Name")
    options = fields.Dict(keys=fields.Str(), values=fields.Nested(CustomOptionSchema))


class ModulesSchema(Schema):
    modules = fields.Nested(ModuleSchema, many=True)


class ModuleTaskRequestSchema(Schema):
    agent = fields.Str(required=True, validate=validate_agent)
    other = fields.Str(required=True, validate=Length(min=1))
    options = fields.Dict(keys=fields.Str(), values=fields.Nested(CustomOptionSchema))


class ModuleTaskResponseSchema(Schema):
    message = fields.Str()
    task_id = fields.Str()
    success = fields.Bool()  # todo vr Necessary? If it fails we won't be sending a 200


class ModuleQuerySchema(Schema):
    class Meta:
        unknown = "EXCLUDE"  # todo vr Because token, move to header? Could also exclude unknown fields on all schemas

    query = fields.Str()


class ModuleQueryRequiredSchema(Schema):
    """
    Like ModuleQuerySchema, but query is required
    """

    class Meta:
        unknown = "EXCLUDE"  # Because token

    query = fields.Str(required=True)
