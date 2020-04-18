from marshmallow import fields
from marshmallow.validate import Length

from lib.api.schemas import EmpireBaseSqlAlchemySchema, EmpireBaseSchema
from lib.database.models import Agent


class AgentSchema(EmpireBaseSqlAlchemySchema):
    class Meta:
        model = Agent
        include_relationships = True
        load_instance = True
        exclude = ('session_key', 'results', 'taskings', 'taskings_executed')

    stale = fields.Bool()


class AgentsSchema(EmpireBaseSchema):
    agents = fields.Nested(AgentSchema, many=True)


class AgentRenameSchema(EmpireBaseSchema):
    new_name = fields.Str(required=True, validate=Length(min=1))


class AgentShellSchema(EmpireBaseSchema):
    command = fields.Str(required=True, validate=Length(min=1))


class AgentTaskResponseSchema(EmpireBaseSchema):
    task_id = fields.Str()


class AgentDownloadSchema(EmpireBaseSchema):
    filename = fields.Str(required=True, validate=Length(min=1))


class AgentUploadSchema(EmpireBaseSchema):
    filename = fields.Str(required=True, validate=Length(min=1))
    data = fields.Str(required=True, validate=Length(min=1))


class AgentResultSchema(EmpireBaseSchema):
    task_id = fields.Str()
    command = fields.Str()
    result = fields.Str()
    user_id = fields.Str()
    username = fields.Str()


class AgentResultsSchema(EmpireBaseSchema):
    results = fields.Nested(AgentResultSchema, many=True)
