from flask.views import MethodView
from flask_smorest import Blueprint

from lib.api.credentials.schemas import CredentialsSchema
from lib.database import models
from lib.database.base import Session

cred_blp = Blueprint(
    'credentials', 'credentials', url_prefix='/api/credentials',
    description='Operations on credentials'
)


@cred_blp.route('/')
class CredentialView(MethodView):

    @cred_blp.response(CredentialsSchema, code=200)
    def get(self):
        """
        Returns JSON describing the credentials stored in the backend database.
        """
        credentials = Session().query(models.Credential).all()

        return {'credentials': credentials}
