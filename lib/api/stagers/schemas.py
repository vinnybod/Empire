from marshmallow import Schema, fields
from marshmallow.validate import Length

# TODO Duplicate of ListenerOptionSchema
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
    stager_name = fields.Str(required=True, validate=Length(min=1))
    listener = fields.Str(required=True, validate=Length(min=1))


class GenerateStagerResponseSchema(Schema):
    stager_name = fields.Str()
    output = fields.Str()
    outfile = fields.Str()
