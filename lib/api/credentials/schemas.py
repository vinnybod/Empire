from marshmallow import fields

from lib.api.schemas import EmpireBaseSqlAlchemySchema, EmpireBaseSchema
from lib.database.models import Credential


class CredentialSchema(EmpireBaseSqlAlchemySchema):
    class Meta:
        model = Credential
        include_relationships = True
        load_instance = True


class CredentialsSchema(EmpireBaseSchema):
    credentials = fields.Nested(CredentialSchema, many=True)
