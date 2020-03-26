from marshmallow import Schema, fields

from lib.api.schemas import CamelCaseSqlAlchemyAutoSchema
from lib.database.models import Config


class ConfigSchema(CamelCaseSqlAlchemyAutoSchema):
    class Meta:
        model = Config
        include_relationships = True
        load_instance = True


class VersionSchema(Schema):
    version = fields.Str()
