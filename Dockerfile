FROM node:20-alpine AS frontend-builder
WORKDIR /app
COPY mj1-app/package*.json ./
RUN npm ci
COPY mj1-app/ ./
RUN npm run build

FROM python:3.11-slim
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy Python requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY mj1_proxy.py .
COPY --from=frontend-builder /app/dist ./mj1-app/dist

# Expose port
EXPOSE 8001

# Run the application (Render sets PORT env variable)
CMD uvicorn mj1_proxy:app --host 0.0.0.0 --port ${PORT:-8001}
