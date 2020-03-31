from marshmallow import Schema, fields

from lib.api.schemas import CamelCaseSqlAlchemyAutoSchema
from lib.database.models import Listener


class ListenerOptionSchema(Schema):
    Description = fields.Str()
    Required = fields.Bool()  # todo vr make camelCase
    Value = fields.Str()  # todo vr This is why it is all strings


class ListenerOptionsSchema(Schema):
    listener_options = fields.Dict(keys=fields.Str(), values=fields.Nested(ListenerOptionSchema))


class ListenerSchema(CamelCaseSqlAlchemyAutoSchema):
    class Meta:
        model = Listener
        include_relationships = True
        load_instance = True

    options = fields.Dict(keys=fields.Str(), values=fields.Nested(ListenerOptionSchema))


class ListenersSchema(CamelCaseSqlAlchemyAutoSchema):
    listeners = fields.Nested(ListenerSchema, many=True)


class ListenerTypeSchema(Schema):
    types = fields.List(fields.Str)


class ListenerStartRequestSchema(Schema):
    options = fields.Dict(keys=fields.Str(), values=fields.Str())
