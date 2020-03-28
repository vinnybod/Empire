from marshmallow import Schema, fields

from lib.api.schemas import CamelCaseSqlAlchemyAutoSchema, PickleBlob
from lib.database.models import Listener


class ListenerSchema(CamelCaseSqlAlchemyAutoSchema):
    class Meta:
        model = Listener
        include_relationships = True
        load_instance = True

    options = PickleBlob()


class ListenersSchema(CamelCaseSqlAlchemyAutoSchema):
    listeners = fields.Nested(ListenerSchema, many=True)


class ListenerTypeSchema(Schema):
    types = fields.List(fields.Str)


class ListenerOptionSchema(Schema):
    Description = fields.Str()
    Required = fields.Bool()
    Value = fields.Str()


class ListenerOptionsSchema(Schema):
    listener_options = fields.Dict(keys=fields.Str(), values=fields.Nested(ListenerOptionSchema))


class ListenerStartRequestSchema(Schema):
    options = fields.Dict(keys=fields.Str(), values=fields.Str())
