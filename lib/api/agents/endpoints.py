from flask.views import MethodView
from flask_smorest import Blueprint
from sqlalchemy import or_
from webargs.flaskparser import abort

from lib.api.agents.schemas import AgentsSchema, AgentSchema
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


@agen_blp.route('/<string:agent_name>')
class AgentName(MethodView):

    @agen_blp.response(AgentSchema, code=200)
    def get(self, agent_name):
        """
        Returns JSON describing the agent specified by agent_name.
        """
        agent = Session().query(models.Agent).filter(models.Agent.name == agent_name).first()

        if agent is None:
            abort(404, message='Could not find agent')

        return agent

    @agen_blp.response(code=201)
    def delete(self, agent_name):
        """
        Removes an agent from the controller specified by agent_name.

        WARNING: doesn't kill the agent first! Ensure the agent is dead.
        """
        if agent_name.lower() == "all":
            agents = Session().query(models.Agent).all()
        else:
            agents = Session().query(models.Agent).filter(or_(
                models.Agent.name == agent_name,
                models.Agent.session_id == agent_name
            )).all()

        if not agents or len(agents) == 0:
            return abort(404, message='agent name %s not found' % agent_name)

        for agent in agents:
            Session.delete(agent)
        Session().commit()
