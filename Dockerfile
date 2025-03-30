# Use an official Python runtime as a parent image, slim variant for smaller size
FROM python:3.11-slim

# Set environment variables to prevent Python from writing pyc files and keep output unbuffered
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory in the container
WORKDIR /app

# Install system dependencies
# - build-essential: Common build tools
# - libpq-dev: Needed for psycopg2 (often a dependency of asyncpg or used directly)
# - libgdal-dev, gdal-bin, libgeos-dev, proj-bin, libproj-dev: Required by GeoPandas/GeoAlchemy2 for spatial operations
# Clean up apt lists afterwards to keep the image size down
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    libgdal-dev \
    gdal-bin \
    libgeos-dev \
    proj-bin \
    libproj-dev \
    && apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy the requirements file into the container
COPY requirements.txt .

# Install Python dependencies specified in requirements.txt
# --no-cache-dir reduces image size by not storing the pip cache
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# Expose the port the app runs on (as defined in main.py)
EXPOSE 8000

# Command to run the application using uvicorn
# Use 0.0.0.0 to bind to all interfaces, making it accessible from outside the container
# Do not use reload=True in production
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]