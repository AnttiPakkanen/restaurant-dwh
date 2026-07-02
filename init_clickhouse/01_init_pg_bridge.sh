#!/bin/bash
set -e
sleep 15
clickhouse-client --query="CREATE DATABASE IF NOT EXISTS postgres_dwh ENGINE = PostgreSQL('postgres-db:5432', 'restaurant', '${POSTGRES_USER}', '${POSTGRES_PASSWORD}');" 