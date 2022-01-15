# Dockerfile

# Use an official Python runtime as a parent image
FROM python:3.8.9

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Create directory for the app user
RUN mkdir -p /home/app

# Create the app user
RUN addgroup --system app && adduser --system --group app

# Set work directories
ENV HOME=/home/app
ENV APP_HOME=/home/app/web
RUN mkdir $APP_HOME
WORKDIR $APP_HOME

# Create & activate venv
# ENV VIRTUAL_ENV=$APP_HOME/venv
# RUN python3 -m venv $VIRTUAL_ENV
# NV PATH="$VIRTUAL_ENV/bin:$PATH"
# ENV PYTHONPATH=$APP_HOME

# Allows docker to cache installed dependencies between builds
COPY requirements.txt $APP_HOME
RUN python3 -m pip install --upgrade pip
RUN pip install -r requirements.txt

# Install npm packages
# RUN npm install

# Mounts the application code to the image
COPY . $APP_HOME
COPY entrypoint.sh $APP_HOME/entrypoint.sh

# chown all the files to the app user
RUN chown -R app:app $APP_HOME

# change to the app user
USER app

# RUN celery -A Brotify worker -l info --without-gossip --without-mingle --without-heartbeat -Ofair --pool=solo -D
