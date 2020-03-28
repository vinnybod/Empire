from marshmallow import Schema, fields


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
