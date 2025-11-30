# Quick Start Guide

## Prerequisites

- Python 3.8+
- PostgreSQL (optional, for Task 3)
- Internet connection (for scraping)

## Step-by-Step Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

### 2. Find App IDs

Before scraping, you need to find the actual Google Play Store app IDs:

```bash
python src/scraping/find_app_ids.py
```

Or manually:
1. Go to Google Play Store
2. Search for each bank's app
3. Copy the app ID from the URL
4. Update `src/scraping/scrape_reviews.py` with the correct app IDs

### 3. Run the Pipeline

**Complete pipeline (recommended):**
```bash
python src/main.py
```

**Or run tasks individually:**

```bash
# Task 1: Scrape and preprocess
python src/scraping/scrape_reviews.py
python src/preprocessing/preprocess_reviews.py

# Task 2: Analyze
python src/analysis/sentiment_analysis.py
python src/analysis/thematic_analysis.py

# Task 3: Database (optional)
python src/database/db_setup.py
python src/database/insert_data.py

# Task 4: Visualize and report
python src/visualization/create_visualizations.py
python src/analysis/generate_insights.py
```

## Expected Output

After running the pipeline, check:

- ✅ `data/processed/reviews_processed.csv` - Cleaned data
- ✅ `data/processed/reviews_with_sentiment.csv` - With sentiment scores
- ✅ `data/processed/reviews_with_themes.csv` - With themes
- ✅ `reports/*.png` - Visualizations
- ✅ `reports/insights_report.md` - Insights and recommendations

## Troubleshooting

### Scraping Issues
- **No reviews found**: Check if app IDs are correct
- **Rate limiting**: The script includes delays, but you may need to increase them

### Sentiment Analysis Issues
- **DistilBERT not loading**: Falls back to VADER automatically
- **Slow processing**: Sentiment analysis can take time for large datasets

### Database Issues
- **Connection error**: Check PostgreSQL is running and credentials in `.env`
- **Table not found**: Run `python src/database/db_setup.py` first

## Next Steps

1. Review the generated visualizations in `reports/`
2. Read the insights report: `reports/insights_report.md`
3. Customize theme identification in `src/analysis/thematic_analysis.py`
4. Add more visualizations as needed

