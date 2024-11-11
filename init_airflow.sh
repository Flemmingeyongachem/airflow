#!/bin/sh

# Initialize the Airflow database
airflow db upgrade

# Create the Airflow admin user
airflow users create \
    --username admin \
    --password admin \
    --firstname admin \
    --lastname admin \
    --role Admin \
    --email admin@example.com
