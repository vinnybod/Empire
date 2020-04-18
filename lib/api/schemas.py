from marshmallow import Schema, fields
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

# TODO vr for all schemas, ignore extra fields.


def camelcase(s):
    parts = iter(s.split("_"))
    return next(parts) + "".join(i.title() for i in parts)


class EmpireBaseSqlAlchemySchema(SQLAlchemyAutoSchema):
    """
    This is the base schema for converting SqlAlchemy objects to api objects.
    Any changes that we want to apply across the board can be added here.
    """
    class Meta:
        # Ordered properties external representation
        ordered = True

    # camelCase properties for external representation, snake_case for internal representation
    def on_bind_field(self, field_name, field_obj):
        field_obj.data_key = camelcase(field_obj.data_key or field_name)


class EmpireBaseSchema(Schema):
    """
    This is the base schema for generating api request and response objects.
    Any changes that we want to apply across the board can be added here.
    At the moment, property ordering and conversion to camelcase.
    """
    class Meta:
        # Ordered properties external representation
        ordered = True

    # camelCase properties for external representation, snake_case for internal representation
    def on_bind_field(self, field_name, field_obj):
        field_obj.data_key = camelcase(field_obj.data_key or field_name)


class CustomOptionSchema(Schema):
    description = fields.Str(attribute="Description")
    required = fields.Bool(attribute="Required")
    value = fields.Str(attribute="Value")  # todo vr This is why it is all strings. Maybe we should add a type field.
