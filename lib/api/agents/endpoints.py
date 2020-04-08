import base64
import hashlib

from flask.views import MethodView
from flask_smorest import Blueprint
from sqlalchemy import or_
from webargs.flaskparser import abort

from lib.api.agents.schemas import AgentsSchema, AgentSchema, AgentRenameSchema, AgentShellSchema, \
    AgentDownloadSchema, AgentResultsSchema, AgentTaskResponseSchema, AgentUploadSchema
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

    @agen_blp.response(code=204)
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

    @agen_blp.response(code=204)
    def delete(self, agent_name):
        """
        Removes an agent from the controller specified by agent_name.

        WARNING: doesn't kill the agent first! Ensure the agent is dead.
        """
        agent = Session().query(models.Agent).filter(or_(
            models.Agent.name == agent_name,
            models.Agent.session_id == agent_name
        )).first()

        if not agent:
            return abort(404, message='agent name %s not found' % agent_name)

        Session.delete(agent)
        Session().commit()


@agen_blp.route('/<string:agent_name>/rename')
class AgentRename(MethodView):

    @agen_blp.arguments(AgentRenameSchema)
    @agen_blp.response(AgentSchema, code=200)
    def put(self, data, agent_name):
        """
        Renames the specified agent.
        """
        new_name = data['new_name']
        agent = Session().query(models.Agent).filter(or_(
            models.Agent.name == agent_name,
            models.Agent.session_id == agent_name
        )).first()

        if not agent:
            abort(404, message='agent name %s not found' % agent_name)

        result = g.main.agents.rename_agent(agent.name, new_name)

        if not result:
            abort(400, message='error in renaming %s to %s, new name may have already been used' % (
                    agent.name, new_name))

        Session().refresh(agent)

        return agent


@agen_blp.route('/<string:agent_name>/shell')
class AgentShell(MethodView):

    @agen_blp.arguments(AgentShellSchema)
    @agen_blp.response(AgentTaskResponseSchema, code=200)
    def post(self, data, agent_name):
        """
        Tasks an the specified agent_name to execute a shell command.
        """
        agent = Session().query(models.Agent).filter(or_(
            models.Agent.name == agent_name,
            models.Agent.session_id == agent_name
        )).first()

        if not agent:
            abort(404, 'agent name %s not found' % (agent_name))

        command = data['command']

        # add task command to agent taskings
        msg = "tasked agent %s to run command %s" % (agent.session_id, command)
        g.main.agents.save_agent_log(agent.session_id, msg)
        task_id = g.main.agents.add_agent_task_db(agent.session_id, "TASK_SHELL", command, uid=g.user.id)

        return {'task_id': task_id}


@agen_blp.route('/<string:agent_name>/download')
class AgentDownload(MethodView):

    @agen_blp.arguments(AgentDownloadSchema)
    @agen_blp.response(AgentTaskResponseSchema, code=200)
    def post(self, data, agent_name):
        """
        Tasks the specified agent to download a file
        """
        agent = Session().query(models.Agent).filter(or_(
            models.Agent.name == agent_name,
            models.Agent.session_id == agent_name
        )).first()

        if agent is None:
            abort(404, 'agent name %s not found' % agent_name)

        file_name = data['filename']

        msg = "Tasked agent to download %s" % file_name
        g.main.agents.save_agent_log(agent.session_id, msg)
        task_id = g.main.agents.add_agent_task_db(agent.session_id, 'TASK_DOWNLOAD', file_name, uid=g.user.id)

        return {'task_id': task_id}


@agen_blp.route('/<string:agent_name>/upload')
class AgentUpload(MethodView):

    @agen_blp.arguments(AgentUploadSchema)
    @agen_blp.response(AgentTaskResponseSchema, code=200)
    def post(self, data, agent_name):
        """
        Tasks the specified agent to upload a file
        """
        agent = Session().query(models.Agent).filter(or_(
            models.Agent.name == agent_name,
            models.Agent.session_id == agent_name
        )).first()

        if agent is None:
            return abort(400, message='agent name %s not found' % agent_name)

        file_data = data['data']
        file_name = data['filename']

        raw_bytes = base64.b64decode(file_data)

        # Todo add validation to schema for this?
        if len(raw_bytes) > 1048576:
            return abort(400, message='file size too large')

        msg = "Tasked agent to upload %s : %s" % (file_name, hashlib.md5(raw_bytes).hexdigest())
        g.main.agents.save_agent_log(agent.session_id, msg)
        data = file_name + "|" + file_data
        task_id = g.main.agents.add_agent_task_db(agent.session_id, 'TASK_UPLOAD', data, uid=g.user.id)

        return {'task_id': task_id}


@agen_blp.route('/<string:agent_name>/kill')
class AgentKill(MethodView):

    @agen_blp.response(AgentTaskResponseSchema, code=201)
    def post(self, agent_name):  # Was a post in the original, maybe should be delete
        """
        Tasks the specified agent to exit.
        """
        agent = Session().query(models.Agent).filter(or_(
            models.Agent.name == agent_name,
            models.Agent.session_id == agent_name
        )).first()

        if agent is None:
            return abort(400, message='agent name %s not found' % agent_name)

        # task the agent to exit
        msg = "tasked agent %s to exit" % (agent.session_id)
        g.main.agents.save_agent_log(agent.session_id, msg)
        g.main.agents.add_agent_task_db(agent.session_id, 'TASK_EXIT', uid=g.user.id)


@agen_blp.route('/<string:agent_name>/clear')
class AgentClear(MethodView):

    @agen_blp.response(code=201)
    def post(self, agent_name):
        """
        Clears the tasking buffer for the specified agent.
        """
        agent = Session().query(models.Agent).filter(or_(
            models.Agent.name == agent_name,
            models.Agent.session_id == agent_name
        )).first()

        if agent is None:
            return abort(400, message='agent name %s not found' % agent_name)

        g.main.agents.clear_agent_tasks_db(agent.session_id)


@agen_blp.route('/<string:agent_name>/results')
class AgentResults(MethodView):

    @agen_blp.response(AgentResultsSchema, code=200)
    def get(self, agent_name):
        """
        Returns JSON describing the agent's results and removes the result field
        from the backend database.
        """
        agent_task_results = []
        agent = Session().query(models.Agent).filter(or_(
            models.Agent.name == agent_name,
            models.Agent.session_id == agent_name
        )).first()

        # Todo this can be done in SQLAlchemy
        agent_results = execute_db_query(conn,
                                        """
            SELECT
                results.id,
                taskings.data AS command,
                results.data AS response,
                users.id as user_id,
                users.username as username
            FROM results
            INNER JOIN taskings ON results.id = taskings.id AND results.agent = taskings.agent
            LEFT JOIN users on results.user_id = users.id
            WHERE results.agent=?;
            """, [agent.session_id])

        results = []
        if len(agent_results) > 0:
            for taskID, command, result, user_id, username in agent_results:
                results.append({'taskID': taskID, 'command': command, 'results': result, 'user_id': user_id,
                                'username': username})

            agent_task_results.append({"AgentName": agent.session_id, "AgentResults": results})
        else:
            agent_task_results.append({"AgentName": agent.session_id, "AgentResults": []})

        return {'results': agent_task_results}

    @agen_blp.response(code=204)
    def delete(self, agent_name):
        """
        Removes the specified agent results field from the backend database.
        """
        agent = Session().query(models.Agent).filter(or_(
            models.Agent.name == agent_name,
            models.Agent.session_id == agent_name
        )).first()

        if agent is None:
            abort(404, message='agent name %s not found' % (agent_name))

        execute_db_query(conn, 'UPDATE agents SET results=? WHERE session_id=?', ['', agent.session_id])
