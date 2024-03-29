import json

from flask_sqlalchemy import SQLAlchemy
from flask import jsonify

database = SQLAlchemy()


class ReservedList(database.Model):
    __tablename__ = "reserved"

    productID = database.Column(database.Integer, database.ForeignKey("products.id"), nullable=False, primary_key=True)
    orderID = database.Column(database.Integer, database.ForeignKey("orders.id"), nullable=False, primary_key=True)
    wanted = database.Column(database.Integer)
    inStock = database.Column(database.Integer)
    price = database.Column(database.Float)


class Order(database.Model):
    __tablename__ = "orders"

    id = database.Column(database.Integer, primary_key=True)
    customer = database.Column(database.Integer, nullable=False)
    status = database.Column(database.String(256), nullable=False)
    price = database.Column(database.Float, nullable=False)
    timestamp = database.Column(database.DateTime, nullable=False)

    products = database.relationship("ProductSQLA", secondary=ReservedList.__table__, cascade="all, delete-orphan")


class ProductCategorySQLA(database.Model):
    __tablename__ = "product_category"

    id = database.Column(database.Integer, primary_key=True)
    productID = database.Column(database.Integer, database.ForeignKey("products.id"), nullable=False)
    categoryID = database.Column(database.Integer, database.ForeignKey("categories.id"), nullable=False)


class ProductSQLA(database.Model):
    __tablename__ = "products"

    id = database.Column(database.Integer, primary_key=True)
    name = database.Column(database.String(256), nullable=False)
    price = database.Column(database.Float, nullable=False)
    quantity = database.Column(database.Integer, nullable=False)

    categories = database.relationship("CategorySQLA", secondary=ProductCategorySQLA.__table__, back_populates="products", cascade="all, delete-orphan")

    def __repr__(self):
        return self.name + " " + str(self.price) + " " + str(self.quantity)


class CategorySQLA(database.Model):
    __tablename__ = "categories"

    id = database.Column(database.Integer, primary_key=True)
    name = database.Column(database.String(256), nullable=False)

    products = database.relationship("ProductSQLA", secondary=ProductCategorySQLA.__table__, back_populates="categories", cascade="all, delete-orphan")

    def __repr__(self):
        return self.name


class Product:
    def __init__(self, id, name, price, quantity, categories):
        self.categories = categories
        self.id = id
        self.name = name
        self.price = price
        self.quantity = quantity

    def __repr__(self):
        return json.dumps(self.__dict__)


class Category:
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return self.name
