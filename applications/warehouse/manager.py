import json

from flask import Flask, request, Response, make_response, jsonify
from configuration import Configuration
from models import database, Product
import csv
import io
from redis import Redis
from flask_jwt_extended import JWTManager, jwt_required
from decorators import roleCheck

app = Flask(__name__)
app.config.from_object(Configuration)
jwt = JWTManager(app)
productID = 0
categoryID = 0


@app.route("/update", methods=["POST"])
@roleCheck("manager")
@jwt_required()
def update():
    try:
        content = request.files["file"].stream.read().decode("utf-8")
    except:
        obj = {"message": "Field file is missing."}
        return make_response(jsonify(obj), 400)
    stream = io.StringIO(content)
    reader = csv.reader(stream)
    rows = list(csv.reader(stream))
    products = []
    line = 0
    for row in rows:
        if len(row) != 4:
            obj = {"message": f"Incorrect number of values on line {line}."}
            return make_response(jsonify(obj), 400)
        try:
            if float(row[2]) <= 0:
                obj = {"message": f"Incorrect quantity on line {line}."}
                return make_response(jsonify(obj), 400)
        except:
            obj = {"message": f"Incorrect quantity on line {line}."}
            return make_response(jsonify(obj), 400)
        try:
            if float(row[3]) <= 0:
                obj = {"message": f"Incorrect price on line {line}."}
                return make_response(jsonify(obj), 400)
        except:
            obj = {"message": f"Incorrect price on line {line}."}
            return make_response(jsonify(obj), 400)
        line += 1

    global productID
    global categoryID

    for row in rows:
        product = Product(id=productID, name=row[1], quantity=row[2], price=row[3], categories=row[0].split("|"))
        productID += 1
        product = {
            "categories": product.categories,
            "name": product.name,
            "quantity": product.quantity,
            "price": product.price
        }
        products.append(product)
    with Redis(host=Configuration.REDIS_HOST) as redis:
        redis.publish(Configuration.REDIS_PRODUCTS_FOR_REVIEW, json.dumps({"products": products}))

    return Response(status=200)


if __name__ == "__main__":
    database.init_app(app)
    # app.run(debug=True, port=5003)
    app.run ( debug = True, host = "0.0.0.0", port = 5001 );
