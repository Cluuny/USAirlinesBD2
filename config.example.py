# PostgreSQL Database Configuration
# Copy this file to config.py and update with your actual credentials

import os

# Database configuration using environment variables
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "your-database-host.amazonaws.com"),
    "dbname": os.getenv("DB_NAME", "your-database-name"), 
    "user": os.getenv("DB_USER", "your-username"),
    "password": os.getenv("DB_PASS", "your-password"),
    "port": os.getenv("DB_PORT", "5432"),
}

# CSV file path
CSV_FILE_PATH = os.getenv("CSV_FILE_PATH", "archive/US Airline Flight Routes and Fares 1993-2024.csv")

# Additional configuration
BATCH_SIZE = 1000  # Batch size for database inserts
DEBUG_MODE = os.getenv("DEBUG_MODE", "False").lower() == "true" 