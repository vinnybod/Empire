import copy
from os import abort

from flask import g
from flask.views import MethodView
from flask_smorest import Blueprint

from lib.api.modules.schemas import ModuleSchema, ModulesSchema, ModuleTaskResponseSchema, \
    ModuleQuerySchemaRequired, ModuleQuerySchema
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
        modules = []
        query = None
        if 'query' in data:
            query = data['query'].lower()
        for module_name, module in g.main.modules.modules.items():
            if query:
                if (query in module_name.lower()) or (
                        query in ("".join(module.info['Description'])).lower()) or (
                        query in ("".join(module.info['Comments'])).lower()) or (
                        query in ("".join(module.info['Author'])).lower()):
                    modules.append(get_module_info(module_name))
            else:
                modules.append(get_module_info(module_name))

        return {'modules': modules}


@modu_blp.route('/<string:module_name>')
class ModuleName(MethodView):

    @modu_blp.response(ModuleSchema, code=200)
    def get(self, module_name):
        """
        Returns JSON describing the specified currently module.
        """
        if module_name not in g.main.modules.modules:
            abort(404, message='module name %s not found' % module_name)

        module_info = copy.deepcopy(g.main.modules.modules[module_name].info)
        module_info['options'] = g.main.modules.modules[module_name].options
        module_info['Name'] = module_name

        return module_info

    # todo arguments
    @modu_blp.arguments(ModuleSchema)
    @modu_blp.response(ModuleTaskResponseSchema, code=201)
    def post(self, data, module_name):
        """
        Executes a given module name with the specified parameters.
        """

        # ensure the 'Agent' argument is set
        if not data['Agent']:
            abort(400, message="TODO Just validate in the schema")

        if module_name not in g.main.modules.modules:
            return abort(400, message='module name %s not found' % module_name)

        module = g.main.modules.modules[module_name]

        # set all passed module options
        for key, value in data.items():
            if key not in module.options:
                abort(400, message='invalid module option')

            module.options[key]['Value'] = value

        # validate module options
        sessionID = module.options['Agent']['Value']

        for option, values in module.options.items():
            if values['Required'] and ((not values['Value']) or (values['Value'] == '')):
                abort(400, message='required module option missing')

        try:
            # if we're running this module for all agents, skip this validation
            if sessionID.lower() != "all" and sessionID.lower() != "autorun":

                if not g.main.agents.is_agent_present(sessionID):
                    abort(400, message='invalid agent name')

                moduleVersion = float(module.info['MinLanguageVersion'])
                agentVersion = float(g.main.agents.get_language_version_db(sessionID))
                # check if the agent/module PowerShell versions are compatible
                # todo modulePSVersion doesn't exist...
                if moduleVersion > agentVersion:
                    abort(400, message="module requires PS version " + str(
                        modulePSVersion) + " but agent running PS version " + str(agentPSVersion))

        except Exception as e:
            return abort(400, message='exception: %s' % (e))

        # check if the module needs admin privs
        if module.info['NeedsAdmin']:
            # if we're running this module for all agents, skip this validation
            if sessionID.lower() != "all" and sessionID.lower() != "autorun":
                if not g.main.agents.is_agent_elevated(sessionID):
                    abort(400, message='module needs to run in an elevated context')

        # actually execute the module
        moduleData = module.generate()

        if not moduleData or moduleData == "":
            abort(400, message='module produced an empty script')

        try:
            if isinstance(moduleData, bytes):
                moduleData = moduleData.decode('ascii')
        except UnicodeDecodeError:
            abort(400, message='module source contains non-ascii characters')

        moduleData = helpers.strip_powershell_comments(moduleData)
        taskCommand = ""

        # build the appropriate task command and module data blob
        if str(module.info['Background']).lower() == "true":
            # if this module should be run in the background
            extention = module.info['OutputExtension']
            if extention and extention != "":
                # if this module needs to save its file output to the server
                #   format- [15 chars of prefix][5 chars extension][data]
                saveFilePrefix = module_name.split("/")[-1]
                moduleData = saveFilePrefix.rjust(15) + extention.rjust(5) + moduleData
                taskCommand = "TASK_CMD_JOB_SAVE"
            else:
                taskCommand = "TASK_CMD_JOB"

        else:
            # if this module is run in the foreground
            extention = module.info['OutputExtension']
            if module.info['OutputExtension'] and module.info['OutputExtension'] != "":
                # if this module needs to save its file output to the server
                #   format- [15 chars of prefix][5 chars extension][data]
                saveFilePrefix = module_name.split("/")[-1][:15]
                moduleData = saveFilePrefix.rjust(15) + extention.rjust(5) + moduleData
                taskCommand = "TASK_CMD_WAIT_SAVE"
            else:
                taskCommand = "TASK_CMD_WAIT"

        if sessionID.lower() == "all":

            for agent in g.main.agents.get_agents():
                sessionID = agent[1]
                task_id = g.main.agents.add_agent_task_db(sessionID, taskCommand, moduleData, uid=g.user.id)
                msg = "tasked agent %s to run module %s" % (sessionID, module_name)
                g.main.agents.save_agent_log(sessionID, msg)

            msg = "tasked all agents to run module %s" % (module_name)

            return {'success': True, 'task_id': task_id, 'message': msg}

        else:
            # set the agent's tasking in the cache
            task_id = g.main.agents.add_agent_task_db(sessionID, taskCommand, moduleData, uid=g.user.id)

            # update the agent log
            msg = "tasked agent %s to run module %s" % (sessionID, module_name)
            g.main.agents.save_agent_log(sessionID, msg)
            return {'success': True, 'task_id': task_id, 'message': msg}


@modu_blp.route('/filter/name')
class ModuleFilterByName(MethodView):

    @modu_blp.arguments(ModuleQuerySchemaRequired, location='query')
    @modu_blp.response(ModulesSchema, code=200)
    def get(self, data):
        """
          Search the modules with a query on name
          """
        modules = []
        query = data['query'].lower()
        for module_name, module in g.main.modules.modules.items():
            if query in module_name.lower():
                modules.append(get_module_info(module_name))

        return {'modules': modules}


@modu_blp.route('/filter/author')
class ModuleFilterByAuthor(MethodView):

    @modu_blp.arguments(ModuleQuerySchemaRequired, location='query')
    @modu_blp.response(ModulesSchema, code=200)
    def get(self, data):
        """
          Search the modules with a query on name
          """
        modules = []
        query = data['query'].lower()
        for module_name, module in g.main.modules.modules.items():
            if query in ("".join(module.info['Author'])).lower():
                modules.append(get_module_info(module_name))

        return {'modules': modules}


@modu_blp.route('/filter/comments')
class ModuleFilterByComments(MethodView):

    @modu_blp.arguments(ModuleQuerySchemaRequired, location='query')
    @modu_blp.response(ModulesSchema, code=200)
    def get(self, data):
        """
          Search the modules with a query on name
          """
        modules = []
        query = data['query'].lower()
        for module_name, module in g.main.modules.modules.items():
            if query in ("".join(module.info['Comments'])).lower():
                modules.append(get_module_info(module_name))

        return {'modules': modules}


@modu_blp.route('/filter/description')
class ModuleFilterByDescription(MethodView):

    @modu_blp.arguments(ModuleQuerySchemaRequired, location='query')
    @modu_blp.response(ModulesSchema, code=200)
    def get(self, data):
        """
          Search the modules with a query on name
          """
        modules = []
        query = data['query'].lower()
        for module_name, module in g.main.modules.modules.items():
            if query in ("".join(module.info['Description'])).lower():
                modules.append(get_module_info(module_name))

        return {'modules': modules}


def get_module_info(module_name):
    module_info = copy.deepcopy(g.main.modules.modules[module_name].info)
    module_info['options'] = g.main.modules.modules[module_name].options
    module_info['Name'] = module_name
    return module_info
