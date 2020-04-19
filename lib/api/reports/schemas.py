from marshmallow import fields

from lib.api.schemas import EmpireBaseSqlAlchemySchema, EmpireBaseSchema
from lib.database.models import Reporting


class ReportSchema(EmpireBaseSqlAlchemySchema):
    class Meta:
        model = Reporting
        include_relationships = True
        load_instance = True


class ReportsSchema(EmpireBaseSchema):
    reporting = fields.Nested(ReportSchema, many=True)
