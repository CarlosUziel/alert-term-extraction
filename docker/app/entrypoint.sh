#!/bin/sh
set -e

# Start the Uvicorn server, using the GUEST_PORT environment variable
exec uvicorn app.main:app --host 0.0.0.0 --port $GUEST_PORT
