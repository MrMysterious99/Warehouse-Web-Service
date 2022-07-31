import json

from flask import Flask, request, Response, make_response, jsonify
from configuration import Configuration
from applications.models import database, Product
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

            # redis.rpush(Configuration.REDIS_PRODUCTS_FOR_REVIEW_LIST, str(product))
            # print(redis.lpop(Configuration.REDIS_PRODUCTS_LIST).decode("utf-8"))
            # obj = redis.lpop(Configuration.REDIS_PRODUCTS_LIST).decode("utf-8")
            # aloe = json.loads(obj.replace("\'", "\""))
            # print(aloe['name'])


    # update samo treba da posalje daemonu a on ce da dodaje kategorije na ovan nacin ako treba
    # for row in rows:
    #     kategorije = row[0].split("|") #sve kategorije iz jednog reda
    #     with Redis(host=Configuration.REDIS_HOST) as redis:
    #         for kategorija in kategorije: # za svaku kategoriju iz jednog reda:
    #             if redis.exists(Configuration.REDIS_CATEGORY_LIST) == 0:
    #                 category = Category(name=kategorija)
    #                 redis.rpush(Configuration.REDIS_CATEGORY_LIST, str(category))
    #             else:
    #                 if str(redis.lrange(Configuration.REDIS_CATEGORY_LIST, 0, -1)).find(kategorija) == -1:
    #                     category = Category(name=kategorija)
    #                     redis.rpush(Configuration.REDIS_CATEGORY_LIST, str(category))
    #                     # redis.rpush(Configuration.REDIS_CATEGORY_LIST, kategorija)

    return Response(status=200)


if __name__ == "__main__":
    database.init_app(app)
    app.run(debug=True, port=5003)
