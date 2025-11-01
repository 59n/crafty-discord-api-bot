# Use official Python slim image for smaller size
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the bot code
COPY bot.py .

# Run the bot
CMD ["python", "-u", "bot.py"]
