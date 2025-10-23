#!/usr/bin/env python3
"""
Database initialization script for TLX Dashboard
This script:
1. Creates the 'tlx' database if it doesn't exist
2. Runs the schema creation script
3. Imports data from CSV files in db_backup folder
"""

import os
import sys
import csv
import logging
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import time

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def get_admin_db_connection():
    """Get connection to PostgreSQL server (not specific database) for admin operations"""
    config = {
        'host': os.getenv('DB_HOST', 'localhost'),
        'user': os.getenv('DB_USER', 'postgres'),
        'password': os.getenv('DB_PASSWORD', ''),
        'port': os.getenv('DB_PORT', '5432'),
        'database': 'postgres'  # Connect to default postgres database
    }
    
    logger.info(f"Connecting to PostgreSQL server at {config['host']}:{config['port']}")
    
    # Retry connection with backoff
    max_retries = 30
    retry_delay = 2
    
    for attempt in range(max_retries):
        try:
            conn = psycopg2.connect(**config)
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            logger.info("Successfully connected to PostgreSQL server")
            return conn
        except psycopg2.Error as e:
            if attempt < max_retries - 1:
                logger.warning(f"Connection attempt {attempt + 1} failed: {e}. Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
                retry_delay = min(retry_delay * 1.5, 30)  # Exponential backoff, max 30s
            else:
                logger.error(f"Failed to connect after {max_retries} attempts: {e}")
                raise

def get_tlx_db_connection():
    """Get connection to the tlx database"""
    config = {
        'host': os.getenv('DB_HOST', 'localhost'),
        'user': os.getenv('DB_USER', 'postgres'),
        'password': os.getenv('DB_PASSWORD', ''),
        'port': os.getenv('DB_PORT', '5432'),
        'database': 'tlx'
    }
    
    try:
        conn = psycopg2.connect(**config)
        logger.info("Connected to tlx database")
        return conn
    except psycopg2.Error as e:
        logger.error(f"Failed to connect to tlx database: {e}")
        raise

def create_database():
    """Create the tlx database if it doesn't exist"""
    conn = get_admin_db_connection()
    cursor = conn.cursor()
    
    try:
        # Check if database exists
        cursor.execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname = 'tlx'")
        exists = cursor.fetchone()
        
        if exists:
            logger.info("Database 'tlx' already exists")
        else:
            logger.info("Creating database 'tlx'...")
            cursor.execute('CREATE DATABASE tlx')
            logger.info("Database 'tlx' created successfully")
            
    except psycopg2.Error as e:
        logger.error(f"Error creating database: {e}")
        raise
    finally:
        cursor.close()
        conn.close()

def run_schema_script():
    """Run the PostgreSQL schema script"""
    schema_file = '/app/coingecko_postgres_schema.sql'
    
    if not os.path.exists(schema_file):
        logger.error(f"Schema file not found: {schema_file}")
        return False
    
    conn = get_tlx_db_connection()
    cursor = conn.cursor()
    
    try:
        logger.info("Running schema creation script...")
        with open(schema_file, 'r') as f:
            schema_sql = f.read()
        
        cursor.execute(schema_sql)
        conn.commit()
        logger.info("Schema created successfully")
        return True
        
    except psycopg2.Error as e:
        logger.error(f"Error running schema script: {e}")
        conn.rollback()
        return False
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

def import_csv_data():
    """Import data from CSV files"""
    csv_folder = '/app/db_backup'
    
    if not os.path.exists(csv_folder):
        logger.warning(f"CSV folder not found: {csv_folder}")
        return True  # Not an error, just no data to import
    
    # Define the CSV to table mapping
    csv_mappings = {
        'liquidity.csv': 'liquidity',
        'lst.csv': 'lst',
        'lst2.csv': 'lst2', 
        'lst3.csv': 'lst3',
        'lst4.csv': 'lst4',
        'price_data.csv': 'price_data',
        'table1.csv': 'table1',
        'table2.csv': 'table2',
        'table3.csv': 'table3',
        'table4.csv': 'table4',
        'trading_view_experiments.csv': 'trading_view_experiments'
    }
    
    conn = get_tlx_db_connection()
    
    for csv_file, table_name in csv_mappings.items():
        csv_path = os.path.join(csv_folder, csv_file)
        
        if not os.path.exists(csv_path):
            logger.warning(f"CSV file not found: {csv_path}")
            continue
            
        # Check if file is empty or has only headers
        with open(csv_path, 'r') as f:
            line_count = sum(1 for line in f)
            
        if line_count <= 1:  # Only header or empty
            logger.info(f"Skipping {csv_file} (empty or only headers)")
            continue
            
        try:
            cursor = conn.cursor()
            
            logger.info(f"Importing {csv_file} into {table_name}...")
            
            # Use COPY command for efficient CSV import
            with open(csv_path, 'r') as f:
                # Skip the header row
                next(f)
                
                cursor.copy_expert(
                    f"COPY {table_name} FROM STDIN WITH CSV",
                    f
                )
            
            conn.commit()
            
            # Get row count
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            logger.info(f"Successfully imported {count} rows into {table_name}")
            
        except psycopg2.Error as e:
            logger.error(f"Error importing {csv_file}: {e}")
            conn.rollback()
            # Continue with other files instead of failing completely
        except Exception as e:
            logger.error(f"Unexpected error importing {csv_file}: {e}")
            conn.rollback()
        finally:
            if cursor:
                cursor.close()
    
    conn.close()
    return True

def check_initialization_needed():
    """Check if initialization has already been completed"""
    try:
        conn = get_admin_db_connection()
        cursor = conn.cursor()
        
        # Check if tlx database exists and has tables
        cursor.execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname = 'tlx'")
        db_exists = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        if not db_exists:
            logger.info("Database 'tlx' does not exist - initialization needed")
            return True
            
        # Check if tables exist in tlx database
        try:
            conn = get_tlx_db_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT COUNT(*) 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name IN ('liquidity', 'lst', 'table1', 'price_data')
            """)
            table_count = cursor.fetchone()[0]
            
            cursor.close()
            conn.close()
            
            if table_count < 4:  # Less than expected tables
                logger.info(f"Only {table_count} tables found - initialization needed")
                return True
            else:
                logger.info("Database appears to be initialized - skipping")
                return False
                
        except psycopg2.Error:
            logger.info("Cannot connect to tlx database - initialization needed")
            return True
            
    except Exception as e:
        logger.warning(f"Error checking initialization status: {e} - proceeding with initialization")
        return True

def main():
    """Main initialization function"""
    logger.info("Starting database initialization...")
    
    # Check if initialization is needed
    if not check_initialization_needed():
        logger.info("Database initialization not needed - exiting")
        return True
    
    try:
        # Step 1: Create database
        create_database()
        
        # Step 2: Run schema script
        if not run_schema_script():
            logger.error("Schema creation failed")
            return False
        
        # Step 3: Import CSV data
        if not import_csv_data():
            logger.error("CSV import failed")
            return False
        
        logger.info("Database initialization completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)