FROM python:3

RUN mkdir -p /opt/src/warehouse
RUN mkdir -p /opt/src/warehouse/daemon
WORKDIR /opt/src/warehouse

COPY applications/warehouse/configuration.py ./configuration.py
COPY applications/warehouse/daemon.py ./daemon.py
COPY applications/warehouse/models.py ./models.py
COPY ./requirements.txt ./requirements.txt
COPY applications/warehouse/decorators.py ./decorators.py

RUN pip install -r ./requirements.txt

ENV PYTHONPATH="/opt/src/warehouse/daemon"

# ENTRYPOINT ["echo", "hello world"]
# ENTRYPOINT ["sleep", "1200"]
ENTRYPOINT ["python", "daemon.py"]
