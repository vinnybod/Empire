from marshmallow import Schema, fields

from lib.api.schemas import CamelCaseSqlAlchemyAutoSchema, CustomOptionSchema
from lib.database.models import Listener


class ListenerOptionsSchema(Schema):
    listener_options = fields.Dict(keys=fields.Str(), values=fields.Nested(CustomOptionSchema))


class ListenerSchema(CamelCaseSqlAlchemyAutoSchema):
    class Meta:
        model = Listener
        include_relationships = True
        load_instance = True

    options = fields.Dict(keys=fields.Str(), values=fields.Nested(CustomOptionSchema))


class ListenersSchema(CamelCaseSqlAlchemyAutoSchema):
    listeners = fields.Nested(ListenerSchema, many=True)


class ListenerTypeSchema(Schema):
    types = fields.List(fields.Str)


class ListenerStartRequestSchema(Schema):
    options = fields.Dict(keys=fields.Str(), values=fields.Str())
