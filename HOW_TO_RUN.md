# How to Run the Project - Step by Step Guide

## Prerequisites Checklist

- [ ] Python 3.8 or higher installed
- [ ] Internet connection (for scraping reviews)
- [ ] PostgreSQL installed (optional, only for Task 3)

## Step 1: Install Dependencies

Open PowerShell or Command Prompt in the project directory and run:

```bash
# Install all required packages
pip install -r requirements.txt

# Download spaCy language model (required for text processing)
python -m spacy download en_core_web_sm
```

**Note:** If you're using a virtual environment, activate it first:
```bash
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

## Step 2: Find Google Play Store App IDs

Before scraping, you need to find the actual app IDs for the three banks.

### Option A: Use the helper script
```bash
python src/scraping/find_app_ids.py
```

This will search for the apps and help you select the correct ones.

### Option B: Find manually
1. Go to [Google Play Store](https://play.google.com/store)
2. Search for each bank's mobile app:
   - "Commercial Bank of Ethiopia mobile"
   - "Bank of Abyssinia mobile"
   - "Dashen Bank mobile"
3. Open each app page
4. Look at the URL - it will be like: `https://play.google.com/store/apps/details?id=com.example.app`
5. Copy the part after `id=` (that's the app ID)

### Update App IDs in Code

Open `src/scraping/scrape_reviews.py` and update the `BANK_APPS` dictionary with the correct app IDs:

```python
BANK_APPS = {
    'CBE': {
        'app_id': 'YOUR_CBE_APP_ID_HERE',  # Replace this
        'app_name': 'Commercial Bank of Ethiopia Mobile',
        'bank_name': 'Commercial Bank of Ethiopia'
    },
    # ... update BOA and Dashen too
}
```

## Step 3: Run the Complete Pipeline

The easiest way is to run everything at once:

```bash
python src/main.py
```

This will automatically:
1. ✅ Scrape reviews from Google Play Store
2. ✅ Preprocess and clean the data
3. ✅ Perform sentiment analysis
4. ✅ Perform thematic analysis
5. ✅ Create visualizations
6. ✅ Generate insights report
7. ✅ Generate Word-friendly report

**Expected time:** 10-30 minutes depending on:
- Number of reviews to scrape
- Internet speed
- Computer performance

## Step 4: Check Output Files

After running, check these directories:

### Data Files
- `data/raw/all_reviews_raw.csv` - Raw scraped reviews
- `data/processed/reviews_processed.csv` - Cleaned data
- `data/processed/reviews_with_sentiment.csv` - With sentiment scores
- `data/processed/reviews_with_themes.csv` - With themes identified

### Reports and Visualizations
- `reports/sentiment_distribution.png` - Sentiment charts
- `reports/rating_distribution.png` - Rating charts
- `reports/theme_distribution.png` - Theme analysis
- `reports/bank_comparison.png` - Bank comparisons
- `reports/wordcloud.png` - Word cloud visualization
- `reports/insights_report.md` - Detailed insights
- `reports/REPORT_FOR_WORD.txt` - **Word-friendly report (copy this to Word!)**

## Alternative: Run Tasks Individually

If you prefer to run tasks one at a time:

### Task 1: Data Collection
```bash
# Scrape reviews
python src/scraping/scrape_reviews.py

# Preprocess data
python src/preprocessing/preprocess_reviews.py
```

### Task 2: Analysis
```bash
# Sentiment analysis
python src/analysis/sentiment_analysis.py

# Thematic analysis
python src/analysis/thematic_analysis.py
```

### Task 3: Database (Optional)
```bash
# First, create a .env file with your PostgreSQL credentials:
# DB_HOST=localhost
# DB_PORT=5432
# DB_USER=postgres
# DB_PASSWORD=your_password
# DB_NAME=bank_reviews

# Setup database
python src/database/db_setup.py

# Insert data
python src/database/insert_data.py
```

### Task 4: Visualizations and Report
```bash
# Create visualizations
python src/visualization/create_visualizations.py

# Generate insights
python src/analysis/generate_insights.py

# Generate Word report
python generate_report.py
```

## Troubleshooting

### Problem: "Module not found" error
**Solution:** Make sure you installed all dependencies:
```bash
pip install -r requirements.txt
```

### Problem: "No reviews found" when scraping
**Solution:** 
- Check if app IDs are correct in `src/scraping/scrape_reviews.py`
- Verify the apps exist on Google Play Store
- Check your internet connection

### Problem: "spaCy model not found"
**Solution:** Download the model:
```bash
python -m spacy download en_core_web_sm
```

### Problem: Sentiment analysis is slow
**Solution:** This is normal! DistilBERT can take time. The script automatically falls back to VADER if DistilBERT fails.

### Problem: Database connection error
**Solution:**
- Make sure PostgreSQL is installed and running
- Check your `.env` file has correct credentials
- Verify the database exists

### Problem: "File not found" errors
**Solution:** Make sure you run tasks in order:
1. Scraping → 2. Preprocessing → 3. Analysis → 4. Visualizations

## Quick Commands Reference

```bash
# Complete pipeline
python src/main.py

# Just generate report (if analysis already done)
python generate_report.py

# Run tests
pytest tests/

# Find app IDs
python src/scraping/find_app_ids.py
```

## What to Do After Running

1. **Open the Word report:**
   - Go to `reports/REPORT_FOR_WORD.txt`
   - Copy all content (Ctrl+A, Ctrl+C)
   - Paste into Microsoft Word (Ctrl+V)
   - Format as needed

2. **Review visualizations:**
   - Check all PNG files in `reports/` folder
   - Insert them into your Word document

3. **Check insights:**
   - Read `reports/insights_report.md` for detailed findings

4. **Verify data quality:**
   - Check `data/processed/` for cleaned data files
   - Ensure you have 1200+ reviews (400+ per bank)

## Need Help?

- Check `README.md` for detailed documentation
- Check `QUICKSTART.md` for quick reference
- Review error messages - they usually indicate what's missing

