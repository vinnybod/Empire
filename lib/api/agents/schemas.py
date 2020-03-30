from marshmallow import fields, Schema
from marshmallow.validate import Length

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


class AgentRenameSchema(Schema):
    new_name = fields.Str(required=True, validate=Length(min=1))


class AgentShellSchema(Schema):
    command = fields.Str(required=True, validate=Length(min=1))


class AgentTaskSingleSchema(Schema):
    task_id = fields.Str()
    agent_name = fields.Str()


class AgentTaskResponseSchema(Schema):
    results = fields.Nested(AgentTaskSingleSchema, many=True)


class AgentDownloadSchema(Schema):
    filename = fields.Str(required=True, validate=Length(min=1))


class AgentUploadSchema(Schema):
    filename = fields.Str(required=True, validate=Length(min=1))
    data = fields.Str(required=True, validate=Length(min=1))


class AgentResultsSchema(Schema):
    pass
