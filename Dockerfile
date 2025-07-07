# Base Image
FROM python:3.12-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Set working directory
WORKDIR /app

# Install system dependencies (optional: depends on your app)
RUN apt-get update && apt-get install -y --no-install-recommends \
    supervisor \
 && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY . /app

# Install Python dependencies
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy Supervisor config
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Expose ports (Gradio: 8080, FastAPI: 8081)
EXPOSE 8080 8081

# Start Supervisor to manage both processes
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
