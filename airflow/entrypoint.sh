#!/bin/bash
set -e

# Clean up any existing PID files and processes
echo "Cleaning up any existing Airflow processes..."
pkill -f "airflow webserver" || true
pkill -f "airflow scheduler" || true
rm -f /opt/airflow/airflow-webserver.pid
rm -f /opt/airflow/airflow-scheduler.pid
# The webserver's gunicorn monitor writes a THIRD pidfile the two lines
# above miss. If a container is ever killed uncleanly (docker kill, a
# host crash), this one survives restarts and makes the webserver refuse
# to start next time ("already running under PID X") even though nothing
# is actually running. Real bug hit and diagnosed in the original course
# repo's copy of this file; fixed here.
rm -f /opt/airflow/airflow-webserver-monitor.pid

# Wait a moment for processes to fully terminate
sleep 2

# Initialize Airflow database
echo "Initializing Airflow database..."
airflow db init

# Create admin user with admin/admin credentials
echo "Creating admin user..."
airflow users create \
    --username admin \
    --firstname Admin \
    --lastname User \
    --role Admin \
    --email admin@example.com \
    --password admin || echo "Admin user already exists"

# Start webserver and scheduler
echo "Starting Airflow webserver and scheduler..."
airflow webserver --port 8080 --daemon &
airflow scheduler