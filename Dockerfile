# Use a lightweight Python image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gettext build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy the application code
COPY . /app

# Expose Gunicorn port
EXPOSE 5000

# Default command to run Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
