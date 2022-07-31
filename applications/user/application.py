from flask import Flask, request, Response, make_response
from configuration import Configuration
from models import *
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, create_refresh_token, get_jwt, \
    get_jwt_identity
from datetime import datetime
from decorators import roleCheck

app = Flask(__name__)
app.config.from_object(Configuration)
jwt = JWTManager(app)


@app.route("/search", methods=["GET"])
@roleCheck("customer")
@jwt_required()
def search():
    name = request.args.get("name")
    category = request.args.get("category")

    if name is None:
        name = ""
    if category is None:
        category = ""

    products = []
    categories = []

    if name != "" or name == "" and category == "":
        products = ProductSQLA.query.filter(ProductSQLA.name.contains(name)).all()
    if category != "" or name == "" and category == "":
        categories = CategorySQLA.query.filter(CategorySQLA.name.contains(category)).all()

    tempProducts = []
    tempCategories = []

    for c in categories:
        tempCategories.append(c.name)

    for product in products:
        for cat in product.categories:
            for kat in categories:
                if cat.name != kat and name != "" and category != "":
                    return jsonify(categories=[], products=[]), 200
        kategorije = []
        for cat in product.categories:
            kategorije.append(cat.name)
        obj = {
            "categories": kategorije,
            "id": product.id,
            "name": product.name,
            "price": product.price,
            "quantity": product.quantity
        }
        #todo ne str nego json!
        tempProducts.append(obj)
        if name != "":
            for cat in product.categories:
                if cat not in tempCategories:
                    if cat.name not in tempCategories:
                        tempCategories.append(cat.name)

    if name == "" and category != "":
        products = ProductSQLA.query.filter(ProductSQLA.name.contains(name)).all()
        for p in products:
            for c in p.categories:
                if c.name.find(category) != -1:
                    kategorije = []
                    for cat in p.categories:
                        kategorije.append(cat.name)
                    obj = {
                        "categories": kategorije,
                        "id": p.id,
                        "name": p.name,
                        "price": p.price,
                        "quantity": p.quantity
                    }
                    tempProducts.append(obj)
                    continue

    return jsonify(categories=tempCategories, products=tempProducts), 200


@app.route("/order", methods=["POST"])
@roleCheck("customer")
@jwt_required()
def order():

    requests = request.json.get("requests", "")

    if len(requests) == 0:
        obj = {"message": "Field requests is missing."}
        return make_response(jsonify(obj), 400)

    # print(requests[0]['id'])
    additionalClaims = get_jwt()
    customer = additionalClaims["id"]

    line = 0
    for req in requests:
        if req.get("id", "") == "":
            obj = {"message": f"Product id is missing for request number {line}."}
            return make_response(jsonify(obj), 400)
        if req.get("quantity", "") == "":
            obj = {"message": f"Product quantity is missing for request number {line}."}
            return make_response(jsonify(obj), 400)
        line += 1

    line = 0
    for req in requests:
        if type(req.get("id", "")) != int:
            obj = {"message": f"Invalid product id for request number {line}."}
            return make_response(jsonify(obj), 400)
        if req.get("id", "") <= 0:
            obj = {"message": f"Invalid product id for request number {line}."}
            return make_response(jsonify(obj), 400)
        if type(req.get("quantity", "")) != int:
            obj = {"message": f"Invalid product quantity for request number {line}."}
            return make_response(jsonify(obj), 400)
        if req.get("quantity", "") <= 0:
            obj = {"message": f"Invalid product quantity for request number {line}."}
            return make_response(jsonify(obj), 400)
    line = 0
    for req in requests:
        if ProductSQLA.query.filter(ProductSQLA.id == req.get("id", "")).first() is None:
            obj = {"message": f"Invalid product for request number {line}."}
            return make_response(jsonify(obj), 400)

    # svi podaci su dobri
    order = Order(customer=customer, status="COMPLETE", price=0, timestamp=datetime.now())
    database.session.add(order)
    database.session.commit()

    produkti = []
    cena = 0
    for req in requests:
        requested_product = ProductSQLA.query.filter(ProductSQLA.id == req.get("id", "")).first()
        obj = {
            "categories": requested_product.categories,
            "name":  requested_product.name,
            "price": requested_product.price,
            "received": 0,
            "requested": req.get("quantity", "")
        }

        cena += obj["requested"] * obj["price"]
        # da li ima dovoljno?
        if requested_product.quantity >= req.get("quantity", ""):
            requested_product.quantity -= req.get("quantity", "")
            obj['received'] = obj['requested']
            rezervacija = ReservedList(productID=requested_product.id, orderID=order.id, wanted=obj['requested'], inStock=obj['requested'], price=requested_product.price)
            database.session.add(rezervacija)
        else:
            order.status = "PENDING"
            obj['received'] = requested_product.quantity
            requested_product.quantity = 0
            rezervacija = ReservedList(productID=requested_product.id, orderID=order.id, wanted=obj['requested'], inStock=obj['received'], price=requested_product.price)
            database.session.add(rezervacija)
        produkti.append(requested_product)

    order.products = produkti
    order.price = cena
    database.session.add(order)
    database.session.commit()
    # print(order)

    return jsonify(id=order.id), 200


@app.route("/status", methods=["GET"])
@roleCheck("customer")
@jwt_required()
def status():
    additionalClaims = get_jwt()
    customer = additionalClaims["id"]

    orders = Order.query.filter(Order.customer == customer).all()
    ret_orders = []
    for o in orders:
        products = []
        for product in o.products:
            received = ReservedList.query.filter(ReservedList.orderID == o.id, ReservedList.productID == product.id).first().inStock
            requested = ReservedList.query.filter(ReservedList.orderID == o.id, ReservedList.productID == product.id).first().wanted
            old_price = ReservedList.query.filter(ReservedList.orderID == o.id, ReservedList.productID == product.id).first().price
            kategorije = []
            for kat in product.categories:
                kategorije.append(kat.name)

            obj = {
                "categories": kategorije,
                "name": product.name,
                "price": old_price,
                "received": received,
                "requested": requested
            }
            products.append(obj)
        order_json = {
            "products": products,
            "price": o.price,
            "status": o.status,
            "timestamp": o.timestamp
        }
        ret_orders.append(order_json)

    # return jsonify(orders=ret_orders), 200

    obj = {"orders": ret_orders}
    return make_response(obj, 200)


if __name__ == "__main__":
    database.init_app(app)
    app.run(debug=True, port=5004)
