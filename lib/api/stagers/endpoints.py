import base64
import copy

from flask import g
from flask.views import MethodView
from flask_smorest import Blueprint
from webargs.flaskparser import abort

from lib.api.stagers.schemas import StagersSchema, StagerSchema, GenerateStagerSchema, GenerateStagerResponseSchema

sta_blp = Blueprint(
    'stagers', 'stagers', url_prefix='/api/stagers',
    description='Operations on stagers'
)


@sta_blp.route('/')
class StagerView(MethodView):

    @sta_blp.response(StagersSchema, code=200)
    def get(self):
        """
        Returns JSON describing all stagers.
        """
        # todo vr post without ending '/' get routed to this get. wtf?
        stagers = []
        for stagerName, stager in g.main.stagers.stagers.items():
            info = copy.deepcopy(stager.info)
            info['options'] = stager.options
            info['Name'] = stagerName
            stagers.append(info)

        return {'stagers': stagers}


@sta_blp.route('/<string:stager_name>')
class StagerName(MethodView):

    @sta_blp.response(StagerSchema, code=200)
    def get(self, stager_name):
        """
        Returns JSON describing the specified stager_name passed.
        """
        # todo Slashes in the path variable that aren't url-encoded are a nono.
        #  We should either start expecting a url-encoded string or name them differently.
        #  Even when url encoding a / to %2f, the routing fails.
        #  https://github.com/pallets/flask/issues/900
        stager_name = stager_name.replace('_', '/', 1)
        if stager_name not in g.main.stagers.stagers:
            abort(404, message='stager name %s not found, make sure to use [os]-[name] format, ie. windows-dll' % stager_name)

        for name, stager in g.main.stagers.stagers.items():
            if name == stager_name:
                info = copy.deepcopy(stager.info)
                info['options'] = stager.options
                info['Name'] = name
                return info

        return {}

    @sta_blp.arguments(GenerateStagerSchema)
    @sta_blp.response(GenerateStagerResponseSchema, code=200)
    def post(self, data, stager_name):
        """
        Generates a stager with the supplied config and returns JSON information
        describing the generated stager, with 'Output' being the stager output.

        Required JSON args:
            StagerName      -   the stager name to generate
            Listener        -   the Listener name to use for the stager
        """
        stager_name = stager_name.replace('_', '/', 1)
        listener = data['listener']

        if stager_name not in g.main.stagers.stagers:
            abort(400, message='stager name %s not found, make sure to use [os]-[name] format, ie. windows-dll' % stager_name)

        if not g.main.listeners.is_listener_valid(listener):
            return abort(400, message='invalid listener ID or name')

        stager = g.main.stagers.stagers[stager_name]

        # set all passed options
        for option, values in data['options'].items():
            if option not in stager.options:
                abort(400, message='Invalid option %s, check capitalization.' % option)
            stager.options[option]['Value'] = values

        # validate stager options
        for option, values in stager.options.items():
            if values['Required'] and ((not values['Value']) or (values['Value'] == '')):
                abort(400, message='required stager options missing')

        stager_options = copy.deepcopy(stager.options)

        if ('OutFile' in stager_options) and (stager_options['OutFile']['Value'] != ''):
            output = stager.generate()
            if isinstance(output, str):
                # if the output was intended for a file, return the base64 encoded text
                output = base64.b64encode(output.encode('UTF-8'))
            else:
                output = base64.b64encode(output)

        else:
            # otherwise return the text of the stager generation
            output = stager.generate()

        return {'stager_name': stager_name, 'output': output, 'options': stager_options}
