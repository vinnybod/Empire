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
class ConfigView(MethodView):

    @sta_blp.response(StagersSchema, code=200)
    def get(self):
        """
        Returns JSON describing all stagers.
        """
        stagers = []
        for stagerName, stager in g.main.stagers.stagers.items():
            info = copy.deepcopy(stager.info)
            info['options'] = stager.options
            info['Name'] = stagerName
            stagers.append(info)

        return {'stagers': stagers}

    @sta_blp.arguments(GenerateStagerSchema)
    @sta_blp.response(GenerateStagerResponseSchema, code=200)
    def post(self, data):
        """
        Generates a stager with the supplied config and returns JSON information
        describing the generated stager, with 'Output' being the stager output.

        Required JSON args:
            StagerName      -   the stager name to generate
            Listener        -   the Listener name to use for the stager
        """
        stager_name = data['stager_name']
        listener = data['listener']

        if stager_name not in g.main.stagers.stagers:
            abort(400, message='stager name %s not found' % stager_name)

        if not g.main.listeners.is_listener_valid(listener):
            return abort(400, message='invalid listener ID or name')

        stager = g.main.stagers.stagers[stager_name]

        # set all passed options
        for option, values in data.items():
            if option != 'stager_name':
                if option not in stager.options:
                    abort(400, message='Invalid option %s, check capitalization.' % option)
                stager.options[option]['Value'] = values

        # validate stager options
        for option, values in stager.options.items():
            if values['Required'] and ((not values['Value']) or (values['Value'] == '')):
                abort(400, message='required stager options missing')

        stager_out = copy.deepcopy(stager.options)

        if ('OutFile' in stager_out) and (stager_out['OutFile']['Value'] != ''):
            if isinstance(stager.generate(), str):
                # if the output was intended for a file, return the base64 encoded text
                stager_out['Output'] = base64.b64encode(stager.generate().encode('UTF-8'))
            else:
                stager_out['Output'] = base64.b64encode(stager.generate())

        else:
            # otherwise return the text of the stager generation
            stager_out['Output'] = stager.generate()

        # TODO This needs some work. other fields are returned besides the outputs.
        #  The schema is not good in the original endpoint.
        return {'stager_name': stager_name, 'output': stager_out['Output'], 'outfile': stager_out['OutFile']}


@sta_blp.route('/<string:stager_name>')
class StagerName(MethodView):

    @sta_blp.response(StagerSchema, code=200)
    def get(self, stager_name):
        """
        Returns JSON describing the specified stager_name passed.
        """
        if stager_name not in g.main.stagers.stagers:
            abort(404, message='stager name %s not found, make sure to use [os]/[name] format, ie. windows/dll' % stager_name)

        for name, stager in g.main.stagers.stagers.items():
            if name == stager_name:
                info = copy.deepcopy(stager.info)
                info['options'] = stager.options
                info['Name'] = name
                return info

        return {}
