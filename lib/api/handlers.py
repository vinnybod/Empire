from functools import wraps

from flask import g
from flask_smorest import abort


def requires_admin(fn):
    """
    Check if a user is an admin by inspecting the g.user object, which comes from the database
    at the start of a request.
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if g.user.admin:
            return fn(*args, **kwargs)
        else:
            abort(401,
                  message='You do not have the required access level required.')

    return wrapper
