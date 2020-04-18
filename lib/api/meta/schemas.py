from marshmallow import fields

from lib.api.schemas import EmpireBaseSqlAlchemySchema, EmpireBaseSchema
from lib.database.models import Config


class ConfigSchema(EmpireBaseSqlAlchemySchema):
    class Meta:
        model = Config
        include_relationships = True
        load_instance = True


class VersionSchema(EmpireBaseSchema):
    version = fields.Str()
