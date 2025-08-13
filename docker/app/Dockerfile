# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Install uv
RUN pip install uv

# Copy dependency definition files
COPY pyproject.toml uv.lock* ./

# Install dependencies
RUN uv pip install --system .

# Copy the project files into the container
COPY ./src /app

# Copy the entrypoint script
COPY ./docker/app/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Set up the port
ARG GUEST_PORT
ENV GUEST_PORT=${GUEST_PORT}
EXPOSE ${GUEST_PORT}

# Run the application
ENTRYPOINT ["/entrypoint.sh"]
CMD []
