"""
PostgreSQL database setup script.
Creates database and tables for bank reviews.
"""

import psycopg2
from psycopg2 import sql
from pathlib import Path
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database configuration
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', '5432'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', 'postgres'),
    'database': os.getenv('DB_NAME', 'bank_reviews')
}

SCHEMA_FILE = Path(__file__).parent.parent.parent / 'sql' / 'schema.sql'


def create_database():
    """Create the database if it doesn't exist."""
    # Connect to default postgres database to create new database
    config = DB_CONFIG.copy()
    config['database'] = 'postgres'  # Connect to default database
    
    try:
        conn = psycopg2.connect(**config)
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Check if database exists
        cursor.execute(
            "SELECT 1 FROM pg_database WHERE datname = %s",
            (DB_CONFIG['database'],)
        )
        
        exists = cursor.fetchone()
        
        if not exists:
            # Create database
            cursor.execute(
                sql.SQL("CREATE DATABASE {}").format(
                    sql.Identifier(DB_CONFIG['database'])
                )
            )
            print(f"✓ Created database: {DB_CONFIG['database']}")
        else:
            print(f"✓ Database already exists: {DB_CONFIG['database']}")
        
        cursor.close()
        conn.close()
        
    except psycopg2.Error as e:
        print(f"Error creating database: {e}")
        print("Please ensure PostgreSQL is running and credentials are correct.")


def execute_schema():
    """Execute schema SQL file."""
    try:
        # Connect to the database
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Read and execute schema file
        if SCHEMA_FILE.exists():
            with open(SCHEMA_FILE, 'r', encoding='utf-8') as f:
                schema_sql = f.read()
            
            # Execute schema (split by semicolons for multiple statements)
            cursor.execute(schema_sql)
            conn.commit()
            
            print("✓ Schema executed successfully")
            
            # Verify tables
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
            """)
            tables = cursor.fetchall()
            print(f"✓ Created tables: {[t[0] for t in tables]}")
            
        else:
            print(f"⚠ Schema file not found: {SCHEMA_FILE}")
        
        cursor.close()
        conn.close()
        
    except psycopg2.Error as e:
        print(f"Error executing schema: {e}")
        raise


def verify_setup():
    """Verify database setup."""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Check banks table
        cursor.execute("SELECT COUNT(*) FROM banks")
        bank_count = cursor.fetchone()[0]
        print(f"✓ Banks table: {bank_count} records")
        
        # Check reviews table
        cursor.execute("SELECT COUNT(*) FROM reviews")
        review_count = cursor.fetchone()[0]
        print(f"✓ Reviews table: {review_count} records")
        
        cursor.close()
        conn.close()
        
    except psycopg2.Error as e:
        print(f"Error verifying setup: {e}")


def main():
    """Main setup function."""
    print("=" * 60)
    print("PostgreSQL Database Setup")
    print("=" * 60)
    
    print("\n1. Creating database...")
    create_database()
    
    print("\n2. Executing schema...")
    execute_schema()
    
    print("\n3. Verifying setup...")
    verify_setup()
    
    print("\n✓ Database setup complete!")


if __name__ == '__main__':
    main()

