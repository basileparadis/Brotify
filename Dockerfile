# Dockerfile

# The first instruction is what image we want to base our container on
# We Use an official Python runtime as a parent image
FROM python:3.8.9

# Allows docker to cache installed dependencies between builds
COPY requirements.txt requirements.txt
RUN python3 -m pip install --upgrade pip
RUN pip3 install -r requirements.txt
RUN rm -rf data

# Mounts the application code to the image
COPY . code
WORKDIR /code

EXPOSE 8000

RUN celery -A Brotify worker -l info --without-gossip --without-mingle --without-heartbeat -Ofair --pool=solo -D
# runs the production server
ENTRYPOINT ["python", "manage.py"]
CMD ["runserver", "0.0.0.0:5000"]
