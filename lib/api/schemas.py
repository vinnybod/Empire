import pickle

from marshmallow import fields
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

from lib.database.models import User, Listener, Agent, Config


def camelcase(s):
    parts = iter(s.split("_"))
    return next(parts) + "".join(i.title() for i in parts)


class CamelCaseSqlAlchemyAutoSchema(SQLAlchemyAutoSchema):
    """Schema that uses camel-case for its external representation
    and snake-case for its internal representation.
    """

    def on_bind_field(self, field_name, field_obj):
        field_obj.data_key = camelcase(field_obj.data_key or field_name)


class PickleBlob(fields.Field):
    """Field that serializes to a title case string and deserializes
    to a lower case string.
    """

    def _serialize(self, value, attr, obj, **kwargs):
        if value is None:
            return ""
        return pickle.loads(value)

    def _deserialize(self, value, attr, data, **kwargs):
        return value.dumps(value)


class ListenerSchema(CamelCaseSqlAlchemyAutoSchema):
    class Meta:
        model = Listener
        include_relationships = True
        load_instance = True

    options = PickleBlob()


class AgentSchema(CamelCaseSqlAlchemyAutoSchema):
    class Meta:
        model = Agent
        include_relationships = True
        load_instance = True

    stale = fields.Bool()


class ConfigSchema(CamelCaseSqlAlchemyAutoSchema):
    class Meta:
        model = Config
        include_relationships = True
        load_instance = True

