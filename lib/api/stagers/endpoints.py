import base64
import copy

from flask import g
from flask.views import MethodView
from flask_smorest import Blueprint
from webargs.flaskparser import abort

from lib.api.stagers.schemas import StagersSchema, StagerSchema

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

    # todo argument
    @sta_blp.arguments(StagerSchema)
    @sta_blp.response(StagerSchema, code=200)
    def post(self, data):
        """
        Generates a stager with the supplied config and returns JSON information
        describing the generated stager, with 'Output' being the stager output.

        Required JSON args:
            StagerName      -   the stager name to generate
            Listener        -   the Listener name to use for the stager
        """
        # TODO dto
        if not data['StagerName'] or not data['Listener']:
            abort(400)

        stagerName = data['StagerName']
        listener = data['Listener']

        if stagerName not in g.main.stagers.stagers:
            abort(404, message='stager name %s not found' % stagerName)

        if not g.main.listeners.is_listener_valid(listener):
            return abort(400, message='invalid listener ID or name')

        stager = g.main.stagers.stagers[stagerName]

        # set all passed options
        for option, values in data.items():
            if option != 'StagerName':
                if option not in stager.options:
                    abort(400, message='Invalid option %s, check capitalization.' % option)
                stager.options[option]['Value'] = values

        # validate stager options
        for option, values in stager.options.items():
            if values['Required'] and ((not values['Value']) or (values['Value'] == '')):
                abort(400, message='required stager options missing')

        stagerOut = copy.deepcopy(stager.options)

        if ('OutFile' in stagerOut) and (stagerOut['OutFile']['Value'] != ''):
            if isinstance(stager.generate(), str):
                # if the output was intended for a file, return the base64 encoded text
                stagerOut['Output'] = base64.b64encode(stager.generate().encode('UTF-8'))
            else:
                stagerOut['Output'] = base64.b64encode(stager.generate())

        else:
            # otherwise return the text of the stager generation
            stagerOut['Output'] = stager.generate()

        return {stagerName: stagerOut}


@sta_blp.route('/<string:stager_name>')
class StagerName(MethodView):

    # todo this should return a single entity
    @sta_blp.response(StagerSchema, code=200)
    def get(self, stager_name):
        """
        Returns JSON describing the specified stager_name passed.
        """
        if stager_name not in g.main.stagers.stagers:
            abort(404, message='stager name %s not found, make sure to use [os]/[name] format, ie. windows/dll' % stager_name)

        stagers = []
        for stagerName, stager in g.main.stagers.stagers.items():
            if stagerName == stager_name:
                info = copy.deepcopy(stager.info)
                info['options'] = stager.options
                info['Name'] = stagerName
                stagers.append(info)

        return {'stagers': stagers}
