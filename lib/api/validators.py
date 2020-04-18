from marshmallow import ValidationError
from sqlalchemy import or_

from lib.database import models
from lib.database.base import Session


def validate_agent(data):
    """
    Validates that an agent exists.
    """
    agent = Session().query(models.Agent).filter(or_(
        models.Agent.name == data,
        models.Agent.session_id == data
    )).first()

    if not agent:
        raise ValidationError('Agent {} not found.'.format(data))


def validate_listener(data):
    """
    Validates that a listener exists.
    """
    listener = Session().query(models.Listener).filter(models.Listener.name == data).first()

    if not listener:
        raise ValidationError('Listener {} not found.'.format(data))

