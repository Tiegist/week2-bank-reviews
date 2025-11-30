"""
Data preprocessing script for bank reviews.
Handles cleaning, normalization, and deduplication.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
import re

RAW_DATA_DIR = Path(__file__).parent.parent.parent / 'data' / 'raw'
PROCESSED_DATA_DIR = Path(__file__).parent.parent.parent / 'data' / 'processed'
PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)


def load_raw_data():
    """Load raw review data from CSV or JSON."""
    # Try multiple possible file names for compatibility
    possible_files = [
        RAW_DATA_DIR / 'reviews_raw.csv',  # From uploaded preprocessing script
        RAW_DATA_DIR / 'all_reviews_raw.csv',  # From our scraper
    ]
    
    for csv_file in possible_files:
        if csv_file.exists():
            df = pd.read_csv(csv_file)
            print(f"Loaded {len(df)} reviews from {csv_file.name}")
            
            # Normalize column names for compatibility
            if 'review_text' in df.columns and 'review' not in df.columns:
                df['review'] = df['review_text']
            if 'review_date' in df.columns and 'date' not in df.columns:
                df['date'] = df['review_date']
            if 'bank_name' in df.columns and 'bank' not in df.columns:
                df['bank'] = df['bank_name']
            
            return df
    
    print(f"Raw data file not found. Tried: {[f.name for f in possible_files]}")
    return None


def remove_duplicates(df):
    """Remove duplicate reviews based on review text and bank."""
    initial_count = len(df)
    df = df.drop_duplicates(subset=['review', 'bank'], keep='first')
    removed = initial_count - len(df)
    print(f"  Removed {removed} duplicate reviews")
    return df


def handle_missing_data(df):
    """Handle missing values in the dataset."""
    initial_count = len(df)
    
    # Remove rows with missing review text
    df = df.dropna(subset=['review'])
    
    # Fill missing ratings with 0 (will be filtered out later)
    df['rating'] = df['rating'].fillna(0).astype(int)
    
    # Remove rows with invalid ratings (should be 1-5)
    df = df[(df['rating'] >= 1) & (df['rating'] <= 5)]
    
    # Fill missing dates with current date
    df['date'] = df['date'].fillna(datetime.now().strftime('%Y-%m-%d'))
    
    removed = initial_count - len(df)
    print(f"  Removed {removed} rows with missing/invalid data")
    return df


def normalize_dates(df):
    """Normalize date formats to YYYY-MM-DD."""
    def parse_date(date_str):
        """Parse various date formats."""
        if pd.isna(date_str):
            return datetime.now().strftime('%Y-%m-%d')
        
        date_str = str(date_str)
        
        # Try parsing common formats
        formats = [
            '%Y-%m-%d',
            '%Y-%m-%d %H:%M:%S',
            '%d/%m/%Y',
            '%m/%d/%Y',
            '%Y-%m-%dT%H:%M:%S',
        ]
        
        for fmt in formats:
            try:
                dt = datetime.strptime(date_str.split()[0], fmt)
                return dt.strftime('%Y-%m-%d')
            except:
                continue
        
        # If all parsing fails, return current date
        return datetime.now().strftime('%Y-%m-%d')
    
    df['date'] = df['date'].apply(parse_date)
    print(f"  Normalized all dates to YYYY-MM-DD format")
    return df


def clean_review_text(df):
    """Basic cleaning of review text."""
    def clean_text(text):
        """Clean individual review text."""
        if pd.isna(text):
            return ''
        
        text = str(text)
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove leading/trailing whitespace
        text = text.strip()
        
        return text
    
    df['review'] = df['review'].apply(clean_text)
    
    # Remove empty reviews after cleaning
    df = df[df['review'].str.len() > 0]
    
    print(f"  Cleaned review text")
    return df


def calculate_data_quality_metrics(df):
    """Calculate data quality metrics."""
    total = len(df)
    missing_review = df['review'].isna().sum()
    missing_rating = df['rating'].isna().sum()
    missing_date = df['date'].isna().sum()
    missing_bank = df['bank'].isna().sum()
    
    error_rate = ((missing_review + missing_rating + missing_date + missing_bank) / (total * 4)) * 100
    
    print(f"\nData Quality Metrics:")
    print(f"  Total reviews: {total}")
    print(f"  Missing review text: {missing_review} ({missing_review/total*100:.2f}%)")
    print(f"  Missing ratings: {missing_rating} ({missing_rating/total*100:.2f}%)")
    print(f"  Missing dates: {missing_date} ({missing_date/total*100:.2f}%)")
    print(f"  Missing bank info: {missing_bank} ({missing_bank/total*100:.2f}%)")
    print(f"  Overall error rate: {error_rate:.2f}%")
    
    return error_rate < 5.0  # KPI: <5% errors


def preprocess_reviews():
    """Main preprocessing function."""
    print("=" * 60)
    print("Review Data Preprocessing")
    print("=" * 60)
    
    # Load raw data
    df = load_raw_data()
    if df is None:
        return None
    
    print(f"\nStarting with {len(df)} reviews")
    
    # Preprocessing steps
    print("\n1. Removing duplicates...")
    df = remove_duplicates(df)
    
    print("\n2. Handling missing data...")
    df = handle_missing_data(df)
    
    print("\n3. Normalizing dates...")
    df = normalize_dates(df)
    
    print("\n4. Cleaning review text...")
    df = clean_review_text(df)
    
    # Select required columns
    required_columns = ['review', 'rating', 'date', 'bank', 'source']
    if all(col in df.columns for col in required_columns):
        df = df[required_columns]
    else:
        print("Warning: Some required columns are missing")
    
    # Calculate quality metrics
    meets_kpi = calculate_data_quality_metrics(df)
    
    # Save processed data
    output_file = PROCESSED_DATA_DIR / 'reviews_processed.csv'
    df.to_csv(output_file, index=False, encoding='utf-8')
    print(f"\n[OK] Saved {len(df)} processed reviews to {output_file}")
    
    if meets_kpi:
        print("[OK] Data quality meets KPI (<5% errors)")
    else:
        print("[WARNING] Data quality does not meet KPI (<5% errors)")
    
    return df


if __name__ == '__main__':
    preprocess_reviews()

