from flask import g
from flask.views import MethodView
from flask_smorest import Blueprint
from webargs.flaskparser import abort

from lib.api.listeners.schemas import ListenerSchema, ListenerTypeSchema, ListenersSchema, ListenerOptionsSchema, \
    ListenerStartRequestSchema
from lib.database import models
from lib.database.base import Session

lis_blp = Blueprint(
    'listeners', 'listeners', url_prefix='/api/listeners',
    description='Operations on listeners'
)


@lis_blp.route('/')
class ListenerView(MethodView):

    @lis_blp.response(ListenersSchema, code=200)
    def get(self):
        """
        Returns JSON describing all currently registered listeners.
        """
        return {'listeners': Session().query(models.Listener).all()}


@lis_blp.route('/<string:listener_name>')
class ListenerName(MethodView):

    @lis_blp.response(ListenerSchema, code=200)
    def get(self, listener_name):
        """
        Returns JSON describing the listener specified by listener_name.
        """
        listener = Session().query(models.Listener).filter(models.Listener.name == listener_name).first()

        if not listener:
            abort(404, message='listener name %s not found' % listener_name)

        return listener

    @lis_blp.response(code=201)
    def delete(self, listener_name):
        """
        Kills the listener specified by listener_name.
        """
        # is there a better way to do this? What if a listener was named all?
        # Optional Param called all=true
        if listener_name.lower() == "all":
            listeners = Session().query(models.Listener).all()
            for listener in listeners:
                g.main.listeners.kill_listener(listener.name)
        else:
            if g.main.listeners.is_listener_valid(listener_name):
                g.main.listeners.kill_listener(listener_name)
            else:
                abort(404, message='listener name %s not found' % listener_name)


@lis_blp.route('/types')
class ListenerTypes(MethodView):

    @lis_blp.response(ListenerTypeSchema, code=200)
    def get(self):
        """
        Returns a list of the loaded listeners that are available for use.
        """
        return {'types': list(g.main.listeners.loadedListeners.keys())}


@lis_blp.route('/options/<string:listener_type>')
class ListenerType(MethodView):

    @lis_blp.response(ListenerOptionsSchema, code=200)
    def get(self, listener_type):
        """
        Returns JSON describing listener options for the specified listener type.
        """
        if listener_type.lower() not in g.main.listeners.loadedListeners:
            abort(404, message='listener type %s not found' % listener_type)

        options = g.main.listeners.loadedListeners[listener_type].options
        return {'listener_options': options}


@lis_blp.route('/<string:listener_type>')
class ListenerStart(MethodView):

    @lis_blp.arguments(ListenerStartRequestSchema)
    @lis_blp.response(ListenerSchema, code=201)
    def post(self, data, listener_type):
        """
        Starts a listener with options supplied in the POST.
        """
        if listener_type.lower() not in g.main.listeners.loadedListeners:
            abort(404, message='listener type %s not found')

        listener_object = g.main.listeners.loadedListeners[listener_type]
        # set all passed options
        for option, values in data.items():
            if isinstance(values, bytes):
                values = values.decode('UTF-8')
            if option == "Name":
                listener_name = values

            returnVal = g.main.listeners.set_listener_option(listener_type, option, values)
            if not returnVal:
                return abort(400, message='error setting listener value %s with option %s' % (option, values))

        g.main.listeners.start_listener(listener_type, listener_object)

        # check to see if the listener was created
        listener_id = g.main.listeners.get_listener_id(listener_name)
        if listener_id:
            return Session().query(models.Listener).filter(models.Listener.id == listener_id).first()
        else:
            abort(500, message='failed to start listener %s' % listener_name)
