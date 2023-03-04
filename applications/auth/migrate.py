from flask import Flask
from configuration import Configuration
from flask_migrate import Migrate, init, migrate, upgrade
from models import database, Role, UserRole, User
from sqlalchemy_utils import database_exists, create_database
import os
import shutil

# dirpath = "/opt/src/auth/migrations"
#
# if os.path.exists(dirpath) and os.path.isdir(dirpath):
#     shutil.rmtree(dirpath)


application = Flask(__name__)
application.config.from_object(Configuration)

migrateObject = Migrate(application, database)

if __name__ == "__main__":

    done = False
    while done == False:
        try:
            if not database_exists(application.config["SQLALCHEMY_DATABASE_URI"]):
                create_database(application.config["SQLALCHEMY_DATABASE_URI"])

            database.init_app(application)

            with application.app_context() as context:
                init()
                migrate(message="Authentication migration")
                upgrade()

                adminRole = Role(name="administrator")
                customer = Role(name="customer")
                manager = Role(name="manager")

                database.session.add(adminRole)
                database.session.add(customer)
                database.session.add(manager)
                database.session.commit()

                admin = User(
                    email="admin@admin.com",
                    password="1",
                    forename="admin",
                    surname="admin",
                    isCustomer=False
                )

                database.session.add(admin)
                database.session.commit()

                userRole = UserRole(
                    userId=admin.id,
                    roleId=adminRole.id
                )

                database.session.add(userRole)
                database.session.commit()
                done = True

        except Exception as exception:
            print(exception)

