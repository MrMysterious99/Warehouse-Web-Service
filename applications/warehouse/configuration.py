import os
from datetime import timedelta;

# databaseUrl = os.environ["DATABASE_URL"]

class Configuration ( ):
    # SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://root:root@{databaseUrl}/warehouse";
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://root:root@localhost:3306/prodavnica"

    JWT_SECRET_KEY = "JWT_SECRET_KEY"
    JWT_ACCESS_TOKEN_EXPIRES = timedelta ( minutes = 60 );
    JWT_REFRESH_TOKEN_EXPIRES = timedelta ( days = 30 );
    # REDIS_HOST = os.environ["REDIS_URL"]
    REDIS_HOST = "localhost"
    REDIS_PRODUCTS_LIST = "products"
    REDIS_CATEGORY_LIST = "categories"
    REDIS_PRODUCTS_FOR_REVIEW = "products_review"
