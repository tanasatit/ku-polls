FROM python:3-alpine

# Pass build arguments
ARG SECRET_KEY
ARG ALLOWED_HOSTS=127.0.0.1,localhost

WORKDIR /app/polls

# Set environment variables
ENV SECRET_KEY=${SECRET_KEY}
ENV DEBUG=True
ENV TIMEZONE=UTC
ENV ALLOWED_HOSTS=${ALLOWED_HOSTS}


# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the app files
COPY . .

# Ensure the entrypoint script is executable
RUN chmod +x ./entrypoint.sh

# Expose the application port
EXPOSE 8000

# Use the entrypoint script
CMD ["./entrypoint.sh"]