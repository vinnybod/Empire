from marshmallow import Schema, fields
from marshmallow.validate import Length


# TODO Duplicate of ListenerOptionSchema
# Should probably put this in the base schema file to be used for listeners and modules
# and also make the letters lowercase.
class StagerOptionSchema(Schema):
    Description = fields.Str()
    Required = fields.Bool()
    Value = fields.Str()


class StagerSchema(Schema):
    Author = fields.List(fields.Str())
    Comments = fields.List(fields.Str())
    Description = fields.Str()
    Name = fields.Str()
    options = fields.Dict(keys=fields.Str(), values=fields.Nested(StagerOptionSchema))


class StagersSchema(Schema):
    stagers = fields.Nested(StagerSchema, many=True)


class GenerateStagerSchema(Schema):
    listener = fields.Str(required=True, validate=Length(min=1))
    options = fields.Dict(keys=fields.Str(), values=fields.Str(), required=True)


class GenerateStagerResponseSchema(Schema):
    stager_name = fields.Str()
    options = fields.Dict(keys=fields.Str(), values=fields.Nested(StagerOptionSchema))
    output = fields.Str()
