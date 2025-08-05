# backend/Dockerfile
# This Dockerfile packages the Python backend application, including the
# Flask server, WebSocket handler, and AI agents.

# Use a specific, slim version of Python for a smaller image size and faster builds.
FROM python:3.9-slim

# Set the working directory inside the container. All subsequent commands
# will run from this path.
WORKDIR /app

# Copy the requirements file first to leverage Docker's layer caching.
# The layer for installing dependencies will only be rebuilt if this file changes.
COPY requirements.txt .

# Install the Python dependencies using pip.
# --no-cache-dir disables the pip cache, which is not needed in a container
# and helps keep the image size down.
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application source code into the container.
COPY . .

# Expose the port that the application will run on.
EXPOSE 5000

# The command to run the application using a production-ready Gunicorn server
# with an Eventlet worker for WebSocket support. This is the standard way to
# run Flask-SocketIO in production.
# -w 1: Use a single worker process.
# --bind 0.0.0.0:5000: Binds the server to all network interfaces on port 5000.
# app:app: Tells Gunicorn to find the `app` object inside the `app.py` file.
CMD ["gunicorn", "--worker-class", "eventlet", "-w", "1", "--bind", "0.0.0.0:5000", "app:app"]
