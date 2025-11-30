"""
Helper script to find Google Play Store app IDs.
This script helps you search for and verify app IDs before scraping.
"""

from google_play_scraper import search
import sys

def search_app(query):
    """Search for apps on Google Play Store."""
    print(f"\nSearching for: {query}")
    print("-" * 60)
    
    try:
        results = search(query, lang='en', country='et', n_hits=5)
        
        if not results:
            print("No results found.")
            return None
        
        print(f"\nFound {len(results)} results:\n")
        
        for i, app in enumerate(results, 1):
            print(f"{i}. {app['title']}")
            print(f"   App ID: {app['appId']}")
            print(f"   Developer: {app.get('developer', 'N/A')}")
            print(f"   Score: {app.get('score', 'N/A')}")
            print(f"   Installs: {app.get('installs', 'N/A')}")
            print()
        
        return results
    except Exception as e:
        print(f"Error searching: {e}")
        return None


def main():
    """Main function to search for bank apps."""
    print("=" * 60)
    print("Google Play Store App ID Finder")
    print("=" * 60)
    
    banks = [
        "Commercial Bank of Ethiopia mobile",
        "Bank of Abyssinia mobile",
        "Dashen Bank mobile"
    ]
    
    app_ids = {}
    
    for bank_query in banks:
        results = search_app(bank_query)
        if results:
            print(f"\nSelect app number for {bank_query} (or press Enter to skip):")
            choice = input().strip()
            
            if choice.isdigit() and 1 <= int(choice) <= len(results):
                selected = results[int(choice) - 1]
                bank_name = bank_query.split()[0]  # Extract bank name
                app_ids[bank_name] = {
                    'app_id': selected['appId'],
                    'app_name': selected['title']
                }
                print(f"✓ Selected: {selected['title']} ({selected['appId']})")
    
    if app_ids:
        print("\n" + "=" * 60)
        print("Selected App IDs:")
        print("=" * 60)
        print("\nUpdate these in src/scraping/scrape_reviews.py:\n")
        print("BANK_APPS = {")
        for bank, info in app_ids.items():
            print(f"    '{bank}': {{")
            print(f"        'app_id': '{info['app_id']}',")
            print(f"        'app_name': '{info['app_name']}',")
            print(f"        'bank_name': '{bank}'")
            print(f"    }},")
        print("}")
    else:
        print("\nNo app IDs selected.")


if __name__ == '__main__':
    main()

