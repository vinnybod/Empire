from marshmallow import Schema, fields

from lib.api.schemas import CustomOptionSchema


class ModuleSchema(Schema):
    author = fields.List(fields.Str(), attribute="Author")
    comments = fields.List(fields.Str(), attribute="Comments")
    description = fields.Str(attribute="Description")
    name = fields.Str(attribute="Name")
    options = fields.Dict(keys=fields.Str(), values=fields.Nested(CustomOptionSchema))


class ModulesSchema(Schema):
    modules = fields.Nested(ModuleSchema, many=True)


class ModuleTaskRequestSchema(Schema):
    agent = fields.Str(required=True) # todo vr min length?
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
