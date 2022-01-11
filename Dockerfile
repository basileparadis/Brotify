# Dockerfile

# Use an official Python runtime as a parent image
FROM python:3.8.9
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Create & activate venv
ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Install npm
#RUN apt-get update -yq \
#    && apt-get -yq install curl gnupg ca-certificates \
#    && curl -L https://deb.nodesource.com/setup_12.x | bash \
#    && apt-get update -yq \
#    && apt-get install -yq \
#        dh-autoreconf=19 \
#        ruby=1:2.5.* \
#        ruby-dev=1:2.5.* \
#        nodejs

# Allows docker to cache installed dependencies between builds
WORKDIR /code
COPY requirements.txt /code/
RUN python3 -m pip install --upgrade pip
RUN pip install -r requirements.txt

# Install npm packages
# RUN npm install

# Mounts the application code to the image
COPY . /code/
COPY entrypoint.sh /entrypoint.sh

# RUN celery -A Brotify worker -l info --without-gossip --without-mingle --without-heartbeat -Ofair --pool=solo -D
