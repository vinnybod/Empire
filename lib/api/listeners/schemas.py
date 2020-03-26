from lib.api.schemas import CamelCaseSqlAlchemyAutoSchema, PickleBlob
from lib.database.models import Listener


class ListenerSchema(CamelCaseSqlAlchemyAutoSchema):
    class Meta:
        model = Listener
        include_relationships = True
        load_instance = True

    options = PickleBlob()
