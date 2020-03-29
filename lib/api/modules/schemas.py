from marshmallow import Schema, fields


# TODO Duplicate of ListenerOptionSchema
class ModuleOptionSchema(Schema):
    Description = fields.Str()
    Required = fields.Bool()
    Value = fields.Str()


class ModuleSchema(Schema):
    Author = fields.List(fields.Str())
    Comments = fields.List(fields.Str())
    Description = fields.Str()
    Name = fields.Str()
    options = fields.Dict(keys=fields.Str(), values=fields.Nested(ModuleOptionSchema))


class ModulesSchema(Schema):
    modules = fields.Nested(ModuleSchema, many=True)


class ModuleTaskResponseSchema(Schema):
    message = fields.Str()
    task_id = fields.Str()
    success = fields.Bool()  # Necessary? If it fails we won't be sending a 200


class ModuleQuerySchema(Schema):
    class Meta:
        unknown = "EXCLUDE"  # Because token
    query = fields.Str()



class ModuleQuerySchemaRequired(Schema):
    class Meta:
        unknown = "EXCLUDE"  # Because token
    query = fields.Str(required=True)
