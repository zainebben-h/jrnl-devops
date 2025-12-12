# Use Python 3.11 as base image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy project files
COPY . .

# Install dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir .

# Create volume for journal data
VOLUME ["/root/.config/jrnl"]

# Set entrypoint
ENTRYPOINT ["jrnl"]

# Default command (show help)
CMD ["--help"]