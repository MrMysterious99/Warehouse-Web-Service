from flask import Flask, request, Response, make_response, jsonify
from configuration import Configuration
from models import database, User, UserRole
from email.utils import parseaddr
import re
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, create_refresh_token, get_jwt, \
    get_jwt_identity
from sqlalchemy import and_
from decorators import roleCheck


app = Flask(__name__)
app.config.from_object(Configuration)


def check_email(email):
    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    return re.fullmatch(regex, email)


@app.route("/register", methods=["POST"])
def register():
    forename = request.json.get("forename", "")
    surname = request.json.get("surname", "")
    email = request.json.get("email", "")
    password = request.json.get("password", "")
    isCustomer = request.json.get("isCustomer", "")

    if len(forename) == 0:
        obj = {"message": "Field forename is missing."}
        return make_response(jsonify(obj), 400)

    if len(surname) == 0:
        obj = {"message": "Field surname is missing."}
        return make_response(jsonify(obj), 400)

    if len(email) == 0:
        obj = {"message": "Field email is missing."}
        return make_response(jsonify(obj), 400)

    if len(password) == 0:
        obj = {"message": "Field password is missing."}
        return make_response(jsonify(obj), 400)

    if isCustomer is None or isCustomer == "":
        obj = {"message": "Field isCustomer is missing."}
        return make_response(jsonify(obj), 400)

    # result = parseaddr(email)
    # if len(result[1]) == 0:
    if not check_email(email):
        obj = {"message": "Invalid email."}
        return make_response(jsonify(obj), 400)

    pass_regex = "^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9]).{8,}$"
    match = re.match(pass_regex, password)

    if match is None:
        obj = {"message": "Invalid password."}
        return make_response(jsonify(obj), 400)

    existing_email = User.query.filter(User.email == email).first()
    if existing_email is not None:
        obj = {"message": "Email already exists."}
        return make_response(jsonify(obj), 400)

    user = User(forename=forename, surname=surname, email=email, password=password, isCustomer=isCustomer)
    database.session.add(user)
    database.session.commit()
    if isCustomer:
        role = 2
    else:
        role = 3

    userRole = UserRole(userId=user.id, roleId=role)
    database.session.add(userRole)
    database.session.commit()

    return Response(status=200)


jwt = JWTManager(app)


@app.route("/login", methods=["POST"])
def login():
    email = request.json.get("email", "")
    password = request.json.get("password", "")

    if len(email) == 0:
        obj = {"message": "Field email is missing."}
        return make_response(jsonify(obj), 400)

    if len(password) == 0:
        obj = {"message": "Field password is missing."}
        return make_response(jsonify(obj), 400)

    # result = parseaddr(email)
    # if len(result[1]) == 0:
    if not check_email(email):
        obj = {"message": "Invalid email."}
        return make_response(jsonify(obj), 400)

    user = User.query.filter(and_(User.email == email, User.password == password)).first()

    if user is None:
        obj = {"message": "Invalid credentials."}
        return make_response(jsonify(obj), 400)

    additionalClaims = {
        "forename": user.forename,
        "surname": user.surname,
        "roles": [str(role) for role in user.roles],
        "email": user.email,
        "id": user.id
    }

    accessToken = create_access_token(identity=user.email, additional_claims=additionalClaims)
    refreshToken = create_refresh_token(identity=user.email, additional_claims=additionalClaims)

    if accessToken is None or refreshToken is None:
        obj = {"message": "Token creation failed."}
        return make_response(jsonify(obj), 400)

    return jsonify(accessToken=accessToken, refreshToken=refreshToken)


@app.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    identity = get_jwt_identity()
    refreshClaims = get_jwt()

    additionalClaims = {
        "forename": refreshClaims["forename"],
        "surname": refreshClaims["surname"],
        "roles": refreshClaims["roles"],
        "email": refreshClaims["email"],
        "id": refreshClaims["id"]
    }

    token = create_access_token(identity=identity, additional_claims=additionalClaims)

    if token is None:
        obj = {"message": "Token creation failed."}
        return make_response(jsonify(obj), 400)

    obj = {"accessToken": create_access_token(identity=identity, additional_claims=additionalClaims)}
    return make_response(obj, 200)


@app.route("/delete", methods=["POST"])
@jwt_required()
@roleCheck("administrator")
def delete():
    identity = get_jwt_identity()
    if identity != "admin@admin.com":
        obj = {"msg": "Missing Authorization Header"}
        return make_response(jsonify(obj), 401)

    try:
        email = request.json.get("email", "")
    except:
        obj = {"message": "Field email is missing."}
        return make_response(jsonify(obj), 401)

    if len(email) == 0:
        obj = {"message": "Field email is missing."}
        return make_response(jsonify(obj), 400)

    if not check_email(email):
        obj = {"message": "Invalid email."}
        return make_response(jsonify(obj), 400)

    existing_email = User.query.filter(User.email == email).first()
    if existing_email is None:
        obj = {"message": "Unknown user."}
        return make_response(jsonify(obj), 400)

    User.query.filter(User.email == email).delete()
    database.session.commit()

    return Response(status=200)


if __name__ == "__main__":
    database.init_app(app)
    app.run(debug=True, host="0.0.0.0", port=5002)
