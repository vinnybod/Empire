from marshmallow import fields, Schema

from lib.api.schemas import CamelCaseSqlAlchemyAutoSchema
from lib.database.models import Agent


class AgentSchema(CamelCaseSqlAlchemyAutoSchema):
    class Meta:
        model = Agent
        include_relationships = True
        load_instance = True

    stale = fields.Bool()


class AgentsSchema(Schema):
    agents = fields.Nested(AgentSchema, many=True)
