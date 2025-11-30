"""
Web scraping script for Google Play Store reviews.
Collects reviews for three Ethiopian banks: CBE, BOA, and Dashen Bank.
"""

import json
import time
from datetime import datetime
from pathlib import Path
from google_play_scraper import app, reviews, Sort
import pandas as pd

# Bank app IDs - Updated with actual app IDs from uploaded config
BANK_APPS = {
    'CBE': {
        'app_id': 'com.combanketh.mobilebanking',  # Actual CBE app ID
        'app_name': 'Commercial Bank of Ethiopia Mobile',
        'bank_name': 'Commercial Bank of Ethiopia'
    },
    'Awash': {
        'app_id': 'com.sc.awashpay',  # Awash Bank app ID
        'app_name': 'Awash Bank Mobile',
        'bank_name': 'Awash Bank'
    },
    'Amharabank': {
        'app_id': 'com.amharabank.Aba_mobile_banking',  # Amharabank app ID
        'app_name': 'Amharabank Mobile',
        'bank_name': 'Amharabank'
    }
}

# Alternative app IDs if the above don't work - these are common patterns
# You may need to search Google Play Store to find the exact app IDs

TARGET_REVIEWS_PER_BANK = 400
OUTPUT_DIR = Path(__file__).parent.parent.parent / 'data' / 'raw'
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def get_app_info(app_id):
    """Get app information from Google Play Store."""
    try:
        app_info = app(app_id, lang='en', country='et')
        return app_info
    except Exception as e:
        print(f"Error fetching app info for {app_id}: {e}")
        return None


def scrape_reviews(app_id, app_name, bank_name, count=TARGET_REVIEWS_PER_BANK):
    """
    Scrape reviews from Google Play Store.
    
    Args:
        app_id: Google Play Store app ID
        app_name: Name of the app
        bank_name: Name of the bank
        count: Number of reviews to scrape
    
    Returns:
        List of review dictionaries
    """
    all_reviews = []
    continuation_token = None
    batch_size = 200  # Scrape in batches
    
    print(f"\nScraping reviews for {bank_name} ({app_name})...")
    
    try:
        while len(all_reviews) < count:
            remaining = count - len(all_reviews)
            current_batch = min(batch_size, remaining)
            
            if continuation_token:
                result, continuation_token = reviews(
                    app_id,
                    lang='en',
                    country='et',
                    sort=Sort.NEWEST,
                    count=current_batch,
                    continuation_token=continuation_token
                )
            else:
                result, continuation_token = reviews(
                    app_id,
                    lang='en',
                    country='et',
                    sort=Sort.NEWEST,
                    count=current_batch
                )
            
            if not result:
                print(f"No more reviews available for {bank_name}")
                break
            
            all_reviews.extend(result)
            print(f"  Collected {len(all_reviews)} reviews so far...")
            
            # Rate limiting - be respectful
            time.sleep(2)
            
            if not continuation_token:
                print(f"No continuation token - reached end of reviews")
                break
        
        print(f"[OK] Successfully scraped {len(all_reviews)} reviews for {bank_name}")
        return all_reviews[:count]  # Return exactly the requested count
        
    except Exception as e:
        print(f"[ERROR] Error scraping reviews for {bank_name}: {e}")
        return []


def format_reviews(reviews_data, bank_name, app_name, bank_code):
    """
    Format scraped reviews into a standardized structure.
    
    Args:
        reviews_data: List of review dictionaries from scraper
        bank_name: Name of the bank
        app_name: Name of the app
        bank_code: Bank code (e.g., 'CBE', 'Awash', 'Amharabank')
    
    Returns:
        List of formatted review dictionaries
    """
    formatted = []
    
    for review in reviews_data:
        # Extract date and format it
        review_date = review.get('at', datetime.now())
        if isinstance(review_date, datetime):
            date_str = review_date.strftime('%Y-%m-%d')
        else:
            date_str = str(review_date)
        
        formatted_review = {
            'review_id': review.get('reviewId', ''),
            'review_text': review.get('content', ''),  # Changed to match preprocessing
            'review': review.get('content', ''),  # Keep both for compatibility
            'rating': review.get('score', 0),
            'review_date': date_str,  # Changed to match preprocessing
            'date': date_str,  # Keep both for compatibility
            'bank_name': bank_name,  # Changed to match preprocessing
            'bank': bank_name,  # Keep both for compatibility
            'bank_code': bank_code,  # Add bank code
            'app_name': app_name,
            'source': 'Google Play Store',
            'user_name': review.get('userName', 'Anonymous'),  # Changed to match preprocessing
            'thumbs_up': review.get('thumbsUpCount', 0),
            'reply_content': review.get('replyContent', None)  # Add reply content
        }
        formatted.append(formatted_review)
    
    return formatted


def save_reviews(reviews_data, bank_code):
    """Save reviews to JSON file."""
    output_file = OUTPUT_DIR / f'{bank_code}_reviews_raw.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(reviews_data, f, indent=2, ensure_ascii=False, default=str)
    print(f"  Saved raw reviews to {output_file}")


def main():
    """Main scraping function."""
    print("=" * 60)
    print("Google Play Store Review Scraper")
    print("=" * 60)
    
    all_formatted_reviews = []
    
    for bank_code, bank_info in BANK_APPS.items():
        app_id = bank_info['app_id']
        app_name = bank_info['app_name']
        bank_name = bank_info['bank_name']
        
        # Try to get app info first to verify app exists
        app_info = get_app_info(app_id)
        if app_info:
            print(f"\nApp found: {app_info.get('title', app_name)}")
            print(f"Current rating: {app_info.get('score', 'N/A')}")
        else:
            print(f"\nWarning: Could not verify app {app_id}")
            print("You may need to update the app_id in the script.")
            print("Continuing anyway...")
        
        # Scrape reviews
        reviews_data = scrape_reviews(app_id, app_name, bank_name, TARGET_REVIEWS_PER_BANK)
        
        if reviews_data:
            # Save raw data
            save_reviews(reviews_data, bank_code)
            
            # Format reviews
            formatted = format_reviews(reviews_data, bank_name, app_name, bank_code)
            all_formatted_reviews.extend(formatted)
        else:
            print(f"[WARNING] No reviews collected for {bank_name}")
    
    # Save combined data
    if all_formatted_reviews:
        df = pd.DataFrame(all_formatted_reviews)
        # Save as both all_reviews_raw.csv and reviews_raw.csv (for compatibility)
        output_csv = OUTPUT_DIR / 'all_reviews_raw.csv'
        df.to_csv(output_csv, index=False, encoding='utf-8')
        # Also save as reviews_raw.csv for the uploaded preprocessing script
        reviews_raw_csv = OUTPUT_DIR / 'reviews_raw.csv'
        df.to_csv(reviews_raw_csv, index=False, encoding='utf-8')
        print(f"\n[OK] Saved {len(all_formatted_reviews)} total reviews to {output_csv}")
        print(f"[OK] Also saved to {reviews_raw_csv} (for preprocessing compatibility)")
        print(f"\nSummary:")
        print(f"  Total reviews: {len(all_formatted_reviews)}")
        print(f"  Reviews per bank:")
        for bank_code in BANK_APPS.keys():
            count = len([r for r in all_formatted_reviews if r['bank'] == BANK_APPS[bank_code]['bank_name']])
            print(f"    {BANK_APPS[bank_code]['bank_name']}: {count}")
    else:
        print("\n[ERROR] No reviews were collected. Please check app IDs and try again.")


if __name__ == '__main__':
    main()

