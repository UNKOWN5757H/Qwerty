# Use lightweight Python image for faster build
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Prevent Python from writing .pyc files and buffering output
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Install system dependencies in one layer for speed
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl bash && \
    rm -rf /var/lib/apt/lists/*

# Copy only requirements first (for caching)
COPY requirements.txt .

# Install Python dependencies quickly using pip cache
RUN pip install --no-cache-dir -r requirements.txt

# Copy rest of your bot files
COPY . .

# Make sure start.sh is executable
RUN chmod +x start.sh

# Expose port (if your bot uses web server)
EXPOSE 8080

# Start your bot
CMD ["bash", "start.sh"]
