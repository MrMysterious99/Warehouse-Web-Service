from flask import jsonify
from flask_jwt_extended import get_jwt, verify_jwt_in_request
from functools import wraps


def roleCheck(role):
    def innerRole(function):
        @wraps(function)
        def decorator(*arguments, **keywordArguments):
            verify_jwt_in_request()
            claims = get_jwt()
            if "role" in claims and role in claims["role"]:
                return function(*arguments, **keywordArguments)
            else:
                return jsonify(msg="Missing Authorization Header"), 401
        return decorator
    return innerRole
