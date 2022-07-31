from datetime import timedelta


class Configuration():
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:root@localhost:3306/prodavnica"
    REDIS_HOST = "localhost"
    REDIS_PRODUCTS_LIST = "products"
    REDIS_CATEGORY_LIST = "categories"
    REDIS_PRODUCTS_FOR_REVIEW = "products_review"
    # REDIS_CATEGORY_PRODUCT_LIST = "cat_prod"
