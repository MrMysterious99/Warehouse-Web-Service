import json

from flask import Flask
from redis import Redis
from configuration import Configuration
from models import *
from operator import and_

app = Flask(__name__)
app.config.from_object(Configuration)
database.init_app(app)

with Redis(host=Configuration.REDIS_HOST) as redis:
    listener = redis.pubsub()
    listener.subscribe(Configuration.REDIS_PRODUCTS_FOR_REVIEW)
    while True:
        message = listener.get_message(True)
        if message:
            with app.app_context() as context:
                redis_array = message.get("data")
                review_products = json.loads(redis_array.decode("utf-8"))
                # print(review_products.get("products")[2])
                products = review_products.get("products")
                for review in products:
                    # print(review)
                    prod = ProductSQLA.query.filter(ProductSQLA.name == review.get("name")).first()
                    if prod is None:
                        # napravim novi proizvod i dodam sve njegove kategorije koje ne postoje
                        # categories = [category.name for category in CategorySQLA.query.all()]
                        change = False
                        kategorije = []
                        for category in review.get("categories"):
                            if CategorySQLA.query.filter(CategorySQLA.name == category).first() is None:
                                nova = CategorySQLA(name=category)
                                database.session.add(nova)
                                change = True
                            kategorije.append(CategorySQLA.query.filter(CategorySQLA.name == category).first())
                        if change:
                            database.session.commit()
                        produkt = ProductSQLA(name=review.get("name"), quantity=review.get("quantity"), price=review.get("price"), categories=kategorije)
                        database.session.add(produkt)
                        database.session.commit()

                    else:
                        # review = trenutni produkt iz zahteva
                        # prod = produkt sa istim imenom u bazi
                        postojece = [category.name for category in prod.categories]
                        postojece.sort()
                        review.get("categories").sort()
                        if postojece == review.get("categories"): # imaju iste kategorije -> quick maths
                            reservations = ReservedList.query.filter(and_(ReservedList.productID == prod.id, ReservedList.wanted > ReservedList.inStock)).all() # nadjem prvi kojem nedostaje ovaj proizvod (FIFO)
                            for row in reservations:
                                if row.wanted - row.inStock > int(review.get("quantity")):
                                    row.inStock += int(review.get("quantity"))
                                    review["quantity"] = 0
                                    continue
                                else:
                                    # print(row)
                                    review["quantity"] = int(review["quantity"]) - (row.wanted - row.inStock)
                                    row.inStock = row.wanted
                                    if ReservedList.query.filter(and_(ReservedList.orderID == row.orderID, ReservedList.inStock < ReservedList.wanted)).first() is None:
                                        # print("hello")
                                        order = Order.query.get(row.orderID)
                                        order.status = "COMPLETE"
                                        database.session.add(order)
                                        database.session.commit()
                                        # print(order)
                                    if review.get("quantity") == 0:
                                        continue
                                database.session.add(row)
                                database.session.commit()
                            # promena cene
                            if int(prod.quantity) + int(review.get("quantity")):
                                newPrice = (prod.quantity * prod.price + int(review.get("quantity")) * float(review.get("price"))) / (prod.quantity + int(review.get("quantity")))
                            else:
                                newPrice = review.get("price")
                            newQuanity = prod.quantity + int(review.get("quantity"))
                            prod.price = newPrice
                            prod.quantity = newQuanity
                            database.session.add(prod)
                            database.session.commit()











