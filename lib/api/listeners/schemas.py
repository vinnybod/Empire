from marshmallow import fields

from lib.api.schemas import EmpireBaseSqlAlchemySchema, CustomOptionSchema, EmpireBaseSchema
from lib.database.models import Listener


class ListenerOptionsSchema(EmpireBaseSchema):
    options = fields.Dict(keys=fields.Str(), values=fields.Nested(CustomOptionSchema))


class ListenerSchema(EmpireBaseSqlAlchemySchema):
    class Meta:
        model = Listener
        include_relationships = True
        load_instance = True

    options = fields.Dict(keys=fields.Str(), values=fields.Nested(CustomOptionSchema))


class ListenersSchema(EmpireBaseSchema):
    listeners = fields.Nested(ListenerSchema, many=True)


class ListenerTypeSchema(EmpireBaseSchema):
    types = fields.List(fields.Str)


class ListenerStartRequestSchema(EmpireBaseSchema):
    options = fields.Dict(keys=fields.Str(), values=fields.Str())
