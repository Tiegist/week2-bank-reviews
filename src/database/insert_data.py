"""
Script to insert cleaned review data into PostgreSQL database.
"""

import pandas as pd
import psycopg2
from psycopg2.extras import execute_batch
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

ANALYSIS_DATA_DIR = Path(__file__).parent.parent.parent / 'data' / 'processed'


def get_bank_id(conn, bank_name):
    """Get bank_id from bank_name."""
    cursor = conn.cursor()
    cursor.execute("SELECT bank_id FROM banks WHERE bank_name = %s", (bank_name,))
    result = cursor.fetchone()
    cursor.close()
    return result[0] if result else None


def insert_reviews(df):
    """Insert reviews into PostgreSQL database."""
    print("=" * 60)
    print("Inserting Reviews into PostgreSQL")
    print("=" * 60)
    
    try:
        # Connect to database
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Get bank IDs
        bank_ids = {}
        for bank_name in df['bank'].unique():
            bank_id = get_bank_id(conn, bank_name)
            if bank_id:
                bank_ids[bank_name] = bank_id
                print(f"✓ Found bank_id {bank_id} for {bank_name}")
            else:
                print(f"⚠ Bank not found in database: {bank_name}")
                print("  Please ensure banks are inserted first.")
        
        if not bank_ids:
            print("✗ No valid banks found. Exiting.")
            cursor.close()
            conn.close()
            return
        
        # Prepare data for insertion
        insert_query = """
            INSERT INTO reviews (
                bank_id, review_text, rating, review_date,
                sentiment_label, sentiment_score, theme, keywords, source
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        records = []
        inserted = 0
        skipped = 0
        
        for _, row in df.iterrows():
            bank_name = row['bank']
            if bank_name not in bank_ids:
                skipped += 1
                continue
            
            bank_id = bank_ids[bank_name]
            
            # Prepare record
            record = (
                bank_id,
                str(row.get('review', '')),
                int(row.get('rating', 0)),
                str(row.get('date', '')),
                str(row.get('sentiment_label', '')) if pd.notna(row.get('sentiment_label')) else None,
                float(row.get('sentiment_score', 0)) if pd.notna(row.get('sentiment_score')) else None,
                str(row.get('theme', '')) if pd.notna(row.get('theme')) else None,
                str(row.get('keywords', '')) if pd.notna(row.get('keywords')) else None,
                str(row.get('source', 'Google Play Store'))
            )
            records.append(record)
        
        # Batch insert
        if records:
            execute_batch(cursor, insert_query, records, page_size=100)
            conn.commit()
            inserted = len(records)
            print(f"\n✓ Inserted {inserted} reviews")
        
        if skipped > 0:
            print(f"⚠ Skipped {skipped} reviews (bank not found)")
        
        # Verify insertion
        cursor.execute("SELECT COUNT(*) FROM reviews")
        total_count = cursor.fetchone()[0]
        print(f"✓ Total reviews in database: {total_count}")
        
        # Count by bank
        cursor.execute("""
            SELECT b.bank_name, COUNT(r.review_id) as review_count
            FROM banks b
            LEFT JOIN reviews r ON b.bank_id = r.bank_id
            GROUP BY b.bank_name
            ORDER BY review_count DESC
        """)
        
        print("\nReviews by Bank:")
        for bank_name, count in cursor.fetchall():
            print(f"  {bank_name}: {count}")
        
        cursor.close()
        conn.close()
        
        # Check KPI
        if inserted >= 1000:
            print("\n✓ Meets KPI (>1,000 reviews inserted)")
        elif inserted >= 400:
            print("\n✓ Meets minimum essential (400+ reviews inserted)")
        else:
            print(f"\n⚠ Does not meet minimum (400+ reviews required, got {inserted})")
        
    except psycopg2.Error as e:
        print(f"✗ Database error: {e}")
        raise
    except Exception as e:
        print(f"✗ Error: {e}")
        raise


def verify_data_integrity():
    """Run SQL queries to verify data integrity."""
    print("\n" + "=" * 60)
    print("Data Integrity Verification")
    print("=" * 60)
    
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Query 1: Count reviews per bank
        print("\n1. Reviews per bank:")
        cursor.execute("""
            SELECT b.bank_name, COUNT(r.review_id) as count
            FROM banks b
            LEFT JOIN reviews r ON b.bank_id = r.bank_id
            GROUP BY b.bank_name
            ORDER BY count DESC
        """)
        for bank_name, count in cursor.fetchall():
            print(f"   {bank_name}: {count}")
        
        # Query 2: Average rating per bank
        print("\n2. Average rating per bank:")
        cursor.execute("""
            SELECT b.bank_name, AVG(r.rating) as avg_rating
            FROM banks b
            JOIN reviews r ON b.bank_id = r.bank_id
            GROUP BY b.bank_name
            ORDER BY avg_rating DESC
        """)
        for bank_name, avg_rating in cursor.fetchall():
            print(f"   {bank_name}: {avg_rating:.2f}")
        
        # Query 3: Sentiment distribution
        print("\n3. Sentiment distribution:")
        cursor.execute("""
            SELECT sentiment_label, COUNT(*) as count
            FROM reviews
            WHERE sentiment_label IS NOT NULL
            GROUP BY sentiment_label
            ORDER BY count DESC
        """)
        for label, count in cursor.fetchall():
            print(f"   {label}: {count}")
        
        # Query 4: Theme distribution
        print("\n4. Top themes:")
        cursor.execute("""
            SELECT theme, COUNT(*) as count
            FROM reviews
            WHERE theme IS NOT NULL AND theme != ''
            GROUP BY theme
            ORDER BY count DESC
            LIMIT 10
        """)
        for theme, count in cursor.fetchall():
            print(f"   {theme}: {count}")
        
        cursor.close()
        conn.close()
        
    except psycopg2.Error as e:
        print(f"Error in verification: {e}")


def main():
    """Main insertion function."""
    # Load data
    input_file = ANALYSIS_DATA_DIR / 'reviews_with_themes.csv'
    
    if not input_file.exists():
        # Try alternative files
        input_file = ANALYSIS_DATA_DIR / 'reviews_with_sentiment.csv'
        if not input_file.exists():
            input_file = ANALYSIS_DATA_DIR / 'reviews_processed.csv'
            if not input_file.exists():
                print(f"Error: No data file found in {ANALYSIS_DATA_DIR}")
                print("Please run preprocessing and analysis first.")
                return
    
    print(f"Loading data from: {input_file}")
    df = pd.read_csv(input_file)
    print(f"Loaded {len(df)} reviews")
    
    # Insert data
    insert_reviews(df)
    
    # Verify integrity
    verify_data_integrity()


if __name__ == '__main__':
    main()

