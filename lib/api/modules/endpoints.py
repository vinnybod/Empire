import copy
from os import abort

from flask import g
from flask.views import MethodView
from flask_smorest import Blueprint

from lib.api.modules.schemas import ModuleSchema, ModulesSchema, ModuleTaskResponseSchema, \
    ModuleQuerySchema, ModuleTaskRequestSchema
from lib.common import helpers

modu_blp = Blueprint(
    'modules', 'modules', url_prefix='/api/modules',
    description='Operations on modules'
)


@modu_blp.route('/')
class ModuleView(MethodView):

    @modu_blp.arguments(ModuleQuerySchema, location='query')
    @modu_blp.response(ModulesSchema, code=200)
    def get(self, data):
        """
        Returns JSON describing all currently loaded modules.
        Optionally, can filter by description, comment, name, and author with the query param.
        """
        # in the future we could do something like. ?query=fuzzysearch&language=powershell&needsAdmin=true
        # for now lets keep it simple stupid
        modules = []
        for module_name, module in g.main.modules.modules.items():
            if 'query' in data:
                query = data['query'].lower()
                if (query in module_name.lower()) or (
                        query in ("".join(module.info['Description'])).lower()) or (
                        query in ("".join(module.info['Comments'])).lower()) or (
                        query in ("".join(module.info['Author'])).lower()):
                    modules.append(get_module_info(module_name))
            else:
                modules.append(get_module_info(module_name))

        return {'modules': modules}


@modu_blp.route('/<string:module_slug>')
class ModuleName(MethodView):

    @modu_blp.response(ModuleSchema, code=200)
    def get(self, module_slug):
        """
        Returns JSON describing the specified currently module.
        """
        # Why we slug: https://github.com/pallets/flask/issues/2507
        # Slashes in the path variable that aren't url-encoded are a nono.
        # Even when url encoding a / to %2f, the routing fails.
        # https://github.com/pallets/flask/issues/900
        if module_slug not in g.main.modules.slug_mappings:
            abort(404, message='module name %s not found' % module_slug)

        return get_module_info(module_slug)

    @modu_blp.arguments(ModuleTaskRequestSchema)
    @modu_blp.response(ModuleTaskResponseSchema, code=201)
    def post(self, data, module_slug):
        """
        Executes a given module name with the specified parameters.
        """
        if module_slug not in g.main.modules.slug_mappings:
            return abort(400, message='module name %s not found' % module_slug)

        module = g.main.modules.modules[g.main.modules.name_from_slug(module_slug)]

        # set all passed module options
        for key, value in data['options'].items():
            if key not in module.options:
                abort(400, message='invalid module option')

            module.options[key]['Value'] = value

        # validate module options
        session_id = module.options['Agent']['Value']

        for option, values in module.options.items():
            if values['Required'] and ((not values['Value']) or (values['Value'] == '')):
                abort(400, message='required module option missing')

        try:
            # if we're running this module for all agents, skip this validation
            if session_id.lower() != "all" and session_id.lower() != "autorun":

                if not g.main.agents.is_agent_present(session_id):
                    abort(400, message='invalid agent name')

                module_version = float(module.info['MinLanguageVersion'])
                agent_version = float(g.main.agents.get_language_version_db(session_id))
                # check if the agent/module PowerShell versions are compatible
                if module_version > agent_version:
                    abort(400, message="module requires PS version " + str(
                        module_version) + " but agent running PS version " + str(agent_version))

        except Exception as e:
            return abort(400, message='exception: %s' % (e))

        # check if the module needs admin privs
        if module.info['NeedsAdmin']:
            # if we're running this module for all agents, skip this validation
            if session_id.lower() != "all" and session_id.lower() != "autorun":
                if not g.main.agents.is_agent_elevated(session_id):
                    abort(400, message='module needs to run in an elevated context')

        # actually execute the module
        module_data = module.generate()

        if not module_data or module_data == "":
            abort(400, message='module produced an empty script')

        try:
            if isinstance(module_data, bytes):
                module_data = module_data.decode('ascii')
        except UnicodeDecodeError:
            abort(400, message='module source contains non-ascii characters')

        module_data = helpers.strip_powershell_comments(module_data)

        # build the appropriate task command and module data blob
        if str(module.info['Background']).lower() == "true":
            # if this module should be run in the background
            extension = module.info['OutputExtension']
            if extension and extension != "":
                # if this module needs to save its file output to the server
                #   format- [15 chars of prefix][5 chars extension][data]
                save_file_prefix = g.modules.name_from_slug(module_slug).split("/")[-1]
                module_data = save_file_prefix.rjust(15) + extension.rjust(5) + module_data
                task_command = "TASK_CMD_JOB_SAVE"
            else:
                task_command = "TASK_CMD_JOB"

        else:
            # if this module is run in the foreground
            extension = module.info['OutputExtension']
            if module.info['OutputExtension'] and module.info['OutputExtension'] != "":
                # if this module needs to save its file output to the server
                #   format- [15 chars of prefix][5 chars extension][data]
                save_file_prefix = g.modules.name_from_slug(module_slug).split("/")[-1][:15]
                module_data = save_file_prefix.rjust(15) + extension.rjust(5) + module_data
                task_command = "TASK_CMD_WAIT_SAVE"
            else:
                task_command = "TASK_CMD_WAIT"

        if session_id.lower() == "all":
            for agent in g.main.agents.get_agents():
                session_id = agent[1]
                task_id = g.main.agents.add_agent_task_db(session_id, task_command, module_data, uid=g.user.id)
                msg = "tasked agent %s to run module %s" % (session_id, module_slug)
                g.main.agents.save_agent_log(session_id, msg)

            msg = "tasked all agents to run module %s" % module_slug

            # todo vr should this be a list of task ids and messages?
            return {'success': True, 'task_id': task_id, 'message': msg}

        else:
            # set the agent's tasking in the cache
            task_id = g.main.agents.add_agent_task_db(session_id, task_command, module_data, uid=g.user.id)

            # update the agent log
            msg = "tasked agent %s to run module %s" % (session_id, module_slug)
            g.main.agents.save_agent_log(session_id, msg)

            return {'success': True, 'task_id': task_id, 'message': msg}


def get_module_info(module_name):
    module_info = copy.deepcopy(g.main.modules.modules[g.main.modules.name_from_slug(module_name)].info)
    module_info['options'] = g.main.modules.modules[module_name].options
    module_info['Name'] = module_name
    return module_info
