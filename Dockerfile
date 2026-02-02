# Dockerfile for Cloud Run deployment
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port for Streamlit (Cloud Run sets PORT env var)
EXPOSE 8080

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Run Streamlit (Cloud Run requires listening on $PORT)
CMD ["sh", "-c", "streamlit run app/streamlit_app.py --server.port=${PORT} --server.address=0.0.0.0 --server.headless=true"]
