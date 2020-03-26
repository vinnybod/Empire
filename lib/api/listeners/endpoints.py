from flask.views import MethodView
from flask_smorest import Blueprint
from webargs.flaskparser import abort

from lib.api.listeners.schemas import ListenerSchema
from lib.database import models
from lib.database.base import Session

lis_blp = Blueprint(
    'listeners', 'listeners', url_prefix='/api/listeners',
    description='Operations on listeners'
)


@lis_blp.route('/')
class ConfigView(MethodView):

    # TODO What's the cleanest way to embed the list so it is { listeners: [] }
    @lis_blp.response(ListenerSchema, code=200)
    def get(self):
        """
        Returns JSON describing all currently registered listeners.
        """
        return Session().query(models.Listener).all()


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

