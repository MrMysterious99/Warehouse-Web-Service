FROM python:3

RUN mkdir -p /opt/src/auth
WORKDIR /opt/src/auth

COPY applications/auth/migrate.py ./migrate.py
COPY applications/auth/configuration.py ./configuration.py
COPY applications/auth/models.py ./models.py
COPY applications/auth/decorators.py ./decorators.py
COPY ./requirements.txt ./requirements.txt

RUN pip install -r ./requirements.txt

ENV PYTHONPATH="/opt/src/auth"

# ENTRYPOINT ["echo", "hello world"]
# ENTRYPOINT ["sleep", "1200"]
ENTRYPOINT ["python", "./migrate.py"]
