from lib.database import models
from lib.database.base import Session


class InternalConfig:
    @staticmethod
    def get(key):
        """Get values from the config table"""
        config = Session().query(models.Config).first()
        if hasattr(config, key):
            return getattr(config, key)
        return ''
