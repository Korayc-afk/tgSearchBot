# Python 3.11 base image
FROM python:3.11-slim

# Working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Create tenants directory
RUN mkdir -p tenants

# Expose port
EXPOSE 5000

# Run database initialization and start app
CMD python database.py && python web_panel_new.py

