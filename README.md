# Week 2 Challenge: Customer Experience Analytics for Fintech Apps

## Project Overview
This project analyzes customer satisfaction with mobile banking apps by collecting and processing user reviews from the Google Play Store for three Ethiopian banks:
- Commercial Bank of Ethiopia (CBE)
- Bank of Abyssinia (BOA)
- Dashen Bank

## Business Objective
Omega Consultancy is supporting banks to improve their mobile apps to enhance customer retention and satisfaction. This project:
- Scrapes user reviews from the Google Play Store
- Analyzes sentiment (positive/negative/neutral) and extracts themes
- Identifies satisfaction drivers and pain points
- Stores cleaned review data in a PostgreSQL database
- Delivers a report with visualizations and actionable recommendations

## Project Structure
```
week2-bank-reviews/
├── config/              # Configuration files
├── data/                # Data storage
│   ├── raw/            # Raw scraped data
│   └── processed/      # Processed data
├── notebooks/          # Jupyter notebooks for exploration
├── reports/            # Generated reports
├── sql/                # SQL scripts
├── src/                # Source code
│   ├── scraping/       # Web scraping scripts
│   ├── preprocessing/  # Data cleaning scripts
│   ├── analysis/       # Sentiment and thematic analysis
│   ├── database/       # Database setup and operations
│   └── visualization/ # Visualization scripts
└── tests/              # Unit tests
```

## Tasks

### Task 1: Data Collection and Preprocessing
- Scrape reviews from Google Play Store (400+ per bank, 1200+ total)
- Preprocess and clean data
- Save as CSV

### Task 2: Sentiment and Thematic Analysis
- Perform sentiment analysis using distilbert or VADER
- Extract keywords and identify themes
- Cluster into 3-5 themes per bank

### Task 3: PostgreSQL Database
- Design and implement database schema
- Store cleaned review data
- Verify data integrity

### Task 4: Insights and Recommendations
- Generate insights and visualizations
- Create actionable recommendations
- Deliver final report

## Setup Instructions

### 1. Install Dependencies

```bash
# Activate virtual environment (if using one)
# On Windows:
venv\Scripts\activate
# On Linux/Mac:
source venv/bin/activate

# Install required packages
pip install -r requirements.txt
```

### 2. Download spaCy Language Model

```bash
python -m spacy download en_core_web_sm
```

### 3. Update App IDs (Important!)

Before scraping, you need to find the actual Google Play Store app IDs for the three banks. 

1. Go to Google Play Store
2. Search for each bank's mobile app
3. Open the app page and check the URL
4. The app ID is in the URL: `https://play.google.com/store/apps/details?id=APP_ID_HERE`

Update the `BANK_APPS` dictionary in `src/scraping/scrape_reviews.py` with the correct app IDs.

### 4. PostgreSQL Setup (Optional for Task 3)

1. Install PostgreSQL from [postgresql.org](https://www.postgresql.org/download/)
2. Create a `.env` file in the project root (copy from `.env.example` if available):
   ```
   DB_HOST=localhost
   DB_PORT=5432
   DB_USER=postgres
   DB_PASSWORD=your_password
   DB_NAME=bank_reviews
   ```
3. Run database setup:
   ```bash
   python src/database/db_setup.py
   ```

## Running the Pipeline

### Option 1: Run Complete Pipeline

```bash
python src/main.py
```

This will run all tasks sequentially:
1. Scrape reviews
2. Preprocess data
3. Perform sentiment analysis
4. Perform thematic analysis
5. Create visualizations
6. Generate insights report

### Option 2: Run Tasks Individually

**Task 1: Scraping and Preprocessing**
```bash
# Scrape reviews
python src/scraping/scrape_reviews.py

# Preprocess data
python src/preprocessing/preprocess_reviews.py
```

**Task 2: Analysis**
```bash
# Sentiment analysis
python src/analysis/sentiment_analysis.py

# Thematic analysis
python src/analysis/thematic_analysis.py
```

**Task 3: Database (Optional)**
```bash
# Setup database
python src/database/db_setup.py

# Insert data
python src/database/insert_data.py
```

**Task 4: Visualizations and Insights**
```bash
# Create visualizations
python src/visualization/create_visualizations.py

# Generate insights
python src/analysis/generate_insights.py
```

## Running Tests

```bash
pytest tests/
```

Or run specific test file:
```bash
python -m pytest tests/test_preprocessing.py
```

## Output Files

After running the pipeline, you'll find:

- **Raw data**: `data/raw/all_reviews_raw.csv`
- **Processed data**: `data/processed/reviews_processed.csv`
- **Analysis results**: `data/processed/reviews_with_sentiment.csv`, `reviews_with_themes.csv`
- **Visualizations**: `reports/*.png` (sentiment_distribution.png, rating_distribution.png, etc.)
- **Insights report**: `reports/insights_report.md`

## Key Dates
- **Interim Submission**: Sunday, 30 Nov 2025, 8:00 PM UTC
- **Final Submission**: Tuesday, 02 Dec 2025, 8:00 PM UTC

## References
- [google-play-scraper](https://github.com/JoMingyu/google-play-scraper)
- [Hugging Face Transformers](https://huggingface.co/docs/transformers)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)

