from sqlalchemy import Column, Integer, Sequence, String, Boolean, BLOB
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from marshmallow import fields
import pickle
from .base import Base


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, Sequence('user_id_seq'), primary_key=True)
    username = Column(String(50), nullable=False)
    password = Column(String(255), nullable=False)
    api_token = Column(String(50))
    last_logon_time = Column(String(50))  # DateTime
    enabled = Column(Boolean, nullable=False)
    admin = Column(Boolean, nullable=False)

    def __repr__(self):
        return "<User(username='%s')>" % (
            self.username)


class Listener(Base):
    __tablename__ = 'listeners'
    id = Column(Integer, Sequence("listener_id_seq"), primary_key=True)
    name = Column(String(255), nullable=False)
    module = Column(String(255), nullable=False)
    listener_type = Column(String(255), nullable=False)
    listener_category = Column(String(255), nullable=False)
    enabled = Column(Boolean, nullable=False)
    options = Column(BLOB, nullable=True)

    def __repr__(self):
        return "<Listener(name='%s')>" % (
            self.name)


def camelcase(s):
    parts = iter(s.split("_"))
    return next(parts) + "".join(i.title() for i in parts)


class CamelCaseSqlAlchemyAutoSchema(SQLAlchemyAutoSchema):
    """Schema that uses camel-case for its external representation
    and snake-case for its internal representation.
    """

    def on_bind_field(self, field_name, field_obj):
        field_obj.data_key = camelcase(field_obj.data_key or field_name)


class PickleBlob(fields.Field):
    """Field that serializes to a title case string and deserializes
    to a lower case string.
    """

    def _serialize(self, value, attr, obj, **kwargs):
        if value is None:
            return ""
        return pickle.loads(value)

    def _deserialize(self, value, attr, data, **kwargs):
        return value.dumps(value)


class UserSchema(CamelCaseSqlAlchemyAutoSchema):
    class Meta:
        model = User
        include_relationships = True
        load_instance = True


class ListenerSchema(CamelCaseSqlAlchemyAutoSchema):
    class Meta:
        model = Listener
        include_relationships = True
        load_instance = True

    options = PickleBlob()

