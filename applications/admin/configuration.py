from datetime import timedelta


class Configuration():
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:root@localhost:3306/prodavnica"
    REDIS_HOST = "localhost"
    REDIS_PRODUCTS_LIST = "products"
    REDIS_CATEGORY_LIST = "categories"
    REDIS_PRODUCTS_FOR_REVIEW = "products_review"
    JWT_SECRET_KEY = "JWT_SECRET_KEY"
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=60)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    # REDIS_CATEGORY_PRODUCT_LIST = "cat_prod"
