from flask import Flask, request, Response, make_response
from configuration import Configuration
from models import *
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, create_refresh_token, get_jwt, \
    get_jwt_identity
from decorators import roleCheck


app = Flask(__name__)
app.config.from_object(Configuration)
jwt = JWTManager(app)


@app.route("/productStatistics", methods=["GET"])
@roleCheck("administrator")
@jwt_required()
def productStatistics():

    reservations = ReservedList.query.all()
    products_for_statistics = []
    statistics = []
    for reservation in reservations:
        if reservation.productID not in products_for_statistics:
            products_for_statistics.append(reservation.productID)

    sold_sum = 0
    inStock_sum = 0

    for product_id in products_for_statistics:
        sold_sum = 0
        inStock_sum = 0
        reserved = ReservedList.query.filter(ReservedList.productID == product_id).all()
        for res in reserved:
            sold_sum += res.wanted
            inStock_sum += res.inStock
        p = ProductSQLA.query.filter(ProductSQLA.id == product_id).first()
        obj = {
            "name": p.name,
            "sold": sold_sum,
            "waiting": sold_sum - inStock_sum
        }
        statistics.append(obj)

    return jsonify(statistics=statistics), 200


def occurance(kategorija):
    sum = 0
    reservations = ReservedList.query.all()
    for reservation in reservations:
        product = ProductSQLA.query.filter(ProductSQLA.id == reservation.productID).first()
        for category in product.categories:
            if kategorija == category:
                sum += reservation.wanted
    # print((kategorija, sum))
    return sum


@app.route("/categoryStatistics", methods=["GET"])
@roleCheck("administrator")
@jwt_required()
def categoryStatistics():
    sortiranje = []
    categories = CategorySQLA.query.all()
    for cat in categories:
        sortiranje.append((cat.name, occurance(cat)))

    sortirana = sorted(sortiranje, key=lambda item: (-item[1], item[0]))

    ans = []
    for sor in sortirana:
        ans.append(sor[0])
    return jsonify(statistics=ans), 200
    # return Response(status=200)


if __name__ == "__main__":
    database.init_app(app)
    app.run(debug=True, port=5005)



