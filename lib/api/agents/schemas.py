from marshmallow import fields, Schema
from marshmallow.validate import Length

from lib.api.schemas import CamelCaseSqlAlchemyAutoSchema, CamelCaseSchema
from lib.database.models import Agent


class AgentSchema(CamelCaseSqlAlchemyAutoSchema):
    class Meta:
        model = Agent
        include_relationships = True
        load_instance = True
        exclude = ('session_key', 'results', 'taskings', 'taskings_executed')

    stale = fields.Bool()


class AgentsSchema(Schema):
    agents = fields.Nested(AgentSchema, many=True)


class AgentRenameSchema(Schema):
    new_name = fields.Str(required=True, validate=Length(min=1))


class AgentShellSchema(Schema):
    command = fields.Str(required=True, validate=Length(min=1))


class AgentTaskResponseSchema(Schema):
    task_id = fields.Str()


class AgentDownloadSchema(Schema):
    filename = fields.Str(required=True, validate=Length(min=1))


class AgentUploadSchema(Schema):
    filename = fields.Str(required=True, validate=Length(min=1))
    data = fields.Str(required=True, validate=Length(min=1))


class AgentResultSchema(CamelCaseSchema):
    task_id = fields.Str()
    command = fields.Str()
    result = fields.Str()
    user_id = fields.Str()
    username = fields.Str()


class AgentResultsSchema(Schema):
    results = fields.Nested(AgentResultSchema, many=True)
