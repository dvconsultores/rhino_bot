# Use the provided base image
FROM andresdom2004/rhino_box:latest

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file first (for caching purposes)
COPY requirements.txt /app/requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy the rest of the application files into the container
COPY . /app

# Expose the Flask app port
EXPOSE 5000

# Default command (can be overridden in docker-compose.yml)
CMD ["sh", "-c", "gunicorn --bind 0.0.0.0:5000 app:app"]
