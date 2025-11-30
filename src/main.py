"""
Main script to run the complete bank review analysis pipeline.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from scraping.scrape_reviews import main as scrape_main
from preprocessing.preprocess_reviews import preprocess_reviews
from analysis.sentiment_analysis import main as sentiment_main
from analysis.thematic_analysis import main as thematic_main
from visualization.create_visualizations import main as viz_main
from analysis.generate_insights import generate_insights_report


def main():
    """Run the complete analysis pipeline."""
    print("=" * 60)
    print("Bank Review Analysis Pipeline")
    print("=" * 60)
    
    # Task 1: Scraping and Preprocessing
    print("\n" + "=" * 60)
    print("TASK 1: Data Collection and Preprocessing")
    print("=" * 60)
    
    print("\nStep 1: Scraping reviews from Google Play Store...")
    try:
        scrape_main()
    except Exception as e:
        print(f"Error in scraping: {e}")
        print("Continuing with existing data if available...")
    
    print("\nStep 2: Preprocessing reviews...")
    try:
        preprocess_reviews()
    except Exception as e:
        print(f"Error in preprocessing: {e}")
        return
    
    # Task 2: Analysis
    print("\n" + "=" * 60)
    print("TASK 2: Sentiment and Thematic Analysis")
    print("=" * 60)
    
    print("\nStep 3: Performing sentiment analysis...")
    try:
        sentiment_main()
    except Exception as e:
        print(f"Error in sentiment analysis: {e}")
        return
    
    print("\nStep 4: Performing thematic analysis...")
    try:
        thematic_main()
    except Exception as e:
        print(f"Error in thematic analysis: {e}")
        return
    
    # Task 3: Database (optional - requires PostgreSQL)
    print("\n" + "=" * 60)
    print("TASK 3: Database Storage (Optional)")
    print("=" * 60)
    print("\nTo insert data into PostgreSQL, run:")
    print("  python src/database/db_setup.py")
    print("  python src/database/insert_data.py")
    
    # Task 4: Visualizations and Insights
    print("\n" + "=" * 60)
    print("TASK 4: Insights and Visualizations")
    print("=" * 60)
    
    print("\nStep 5: Creating visualizations...")
    try:
        viz_main()
    except Exception as e:
        print(f"Error in visualization: {e}")
        return
    
    print("\nStep 6: Generating insights and recommendations...")
    try:
        generate_insights_report()
    except Exception as e:
        print(f"Error in insights generation: {e}")
        return
    
    print("\n" + "=" * 60)
    print("Pipeline Complete!")
    print("=" * 60)
    print("\nOutput files:")
    print("  - Processed data: data/processed/")
    print("  - Visualizations: reports/")
    print("  - Insights report: reports/insights_report.md")
    print("\nTo generate reports:")
    print("  - Interim report: python generate_interim_report.py")
    print("  - Final report: python generate_report.py (if available)")


if __name__ == '__main__':
    main()

