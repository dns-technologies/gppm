#!/bin/bash

sleep 5

python /app/app/backend_pre_start.py

alembic upgrade head

python /app/app/initial_data.py
