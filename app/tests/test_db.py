import os
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

# Connect to default postgres db to manage databases
admin_url = "postgresql://postgres:popsixle@localhost:5432/postgres"

DATABASE_NAME = "water_depot_db"

try:
    engine = create_engine(admin_url, isolation_level="AUTOCOMMIT")
    with engine.connect() as conn:
        # Terminate connections to the database
        conn.execute(text(f"SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = '{DATABASE_NAME}';"))
        # Drop the database if it exists
        conn.execute(text(f"DROP DATABASE IF EXISTS {DATABASE_NAME};"))
        # Create the database
        conn.execute(text(f"CREATE DATABASE {DATABASE_NAME};"))
        print(f"Database {DATABASE_NAME} dropped and recreated successfully!")
except SQLAlchemyError as e:
    print("Failed to manage database:", str(e))
