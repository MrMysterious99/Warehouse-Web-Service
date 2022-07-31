# import os
# import sys
# from pathlib import Path
# now = os.getcwd()
# path = Path(now)
# parent = path.parent.absolute()
# # models_path = os.path.join("models.py", parent)
# models_path = os.path.join(parent, "models.py")
# sys.path.append(models_path)

from flask import request, Blueprint
import io
import csv

productsBlueprint = Blueprint("products", __name__)


