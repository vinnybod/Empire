from flask.views import MethodView
from flask_smorest import Blueprint

from lib.api.agents.schemas import AgentsSchema
from lib.database import models
from lib.database.base import Session

agen_blp = Blueprint(
    'agents', 'agents', url_prefix='/api/agents',
    description='Operations on agents'
)


@agen_blp.route('/')
class AgentView(MethodView):

    @agen_blp.response(AgentsSchema, code=200)
    def get(self):
        """
        Returns JSON describing all currently registered agents.
        """
        return {'agents': Session().query(models.Agent).all()}


@agen_blp.route('/stale')
class AgentStale(MethodView):

    @agen_blp.response(AgentsSchema, code=200)
    def get(self):
        """
        Returns JSON describing all stale agents.
        """
        return {'agents': Session().query(models.Agent).filter(models.Agent.stale == True).all()}

    @agen_blp.response(code=201)
    def delete(self):
        """
        Removes stale agents from the controller.

        WARNING: doesn't kill the agent first! Ensure the agent is dead.
        """
        agents = Session().query(models.Agent).filter(models.Agent.stale == True).all()

        for agent in agents:
            Session().delete(agent)
        Session().commit()
