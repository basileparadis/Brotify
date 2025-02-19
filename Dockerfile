# Use an official Python runtime as a parent image
FROM python:3.8.9

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=5000
ENV HOME=/home/app
ENV APP_HOME=/home/app/web
ENV PATH="/home/app/.local/bin:${PATH}"

# Create the app user
RUN addgroup --system app && adduser --system --group app

# Set work directory
WORKDIR $APP_HOME

# Copy requirements first
COPY requirements.txt .

# Install dependencies as root for system-wide installation
RUN python3 -m pip install --upgrade pip && \
    pip install -r requirements.txt

# Expose the port
EXPOSE 5000

# Copy the project files
COPY . .
COPY entrypoint.sh .

# Make entrypoint executable and fix permissions
RUN chmod +x entrypoint.sh && \
    chown -R app:app $APP_HOME

# Change to the app user
USER app

# Set the entrypoint
ENTRYPOINT ["./entrypoint.sh"]