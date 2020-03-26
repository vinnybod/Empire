import urllib.request as urllib

from flask.views import MethodView
from flask_smorest import Blueprint

from lib.api.meta.schemas import ConfigSchema, VersionSchema
from lib.common import empire
from lib.database import models
from lib.database.base import Session

meta_blp = Blueprint(
    'meta', 'meta', url_prefix='/api/meta',
    description='Meta info'
)


@meta_blp.route('/config')
class ConfigView(MethodView):

    @meta_blp.response(ConfigSchema, code=200)
    def get(self):
        """
        Returns JSON of the current Empire config.
        """
        return Session().query(models.Config).first()


@meta_blp.route('/version')
class VersionView(MethodView):

    @meta_blp.response(VersionSchema, code=200)
    def get(self):
        """
        Returns the current Empire version.
        """
        return {'version': empire.VERSION}
