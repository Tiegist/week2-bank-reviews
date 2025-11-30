"""
Sentiment analysis script for bank reviews.
Uses distilbert-base-uncased-finetuned-sst-2-english or VADER as fallback.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from transformers import pipeline
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import warnings
warnings.filterwarnings('ignore')

PROCESSED_DATA_DIR = Path(__file__).parent.parent.parent / 'data' / 'processed'
ANALYSIS_DATA_DIR = Path(__file__).parent.parent.parent / 'data' / 'processed'
ANALYSIS_DATA_DIR.mkdir(parents=True, exist_ok=True)

# Try to use distilbert, fallback to VADER if not available
USE_DISTILBERT = True
sentiment_pipeline = None
vader_analyzer = None


def initialize_sentiment_analyzer():
    """Initialize sentiment analysis model."""
    global sentiment_pipeline, vader_analyzer, USE_DISTILBERT
    
    try:
        if USE_DISTILBERT:
            print("Initializing DistilBERT sentiment analyzer...")
            sentiment_pipeline = pipeline(
                "sentiment-analysis",
                model="distilbert-base-uncased-finetuned-sst-2-english",
                device=-1  # Use CPU
            )
            print("✓ DistilBERT loaded successfully")
            return True
    except Exception as e:
        print(f"Could not load DistilBERT: {e}")
        print("Falling back to VADER sentiment analyzer...")
        USE_DISTILBERT = False
    
    # Fallback to VADER
    vader_analyzer = SentimentIntensityAnalyzer()
    print("✓ VADER sentiment analyzer initialized")
    return False


def analyze_sentiment_distilbert(text):
    """Analyze sentiment using DistilBERT."""
    if not text or pd.isna(text) or len(str(text).strip()) == 0:
        return 'NEUTRAL', 0.5
    
    try:
        # Truncate very long texts (DistilBERT has token limits)
        text = str(text)[:512]
        result = sentiment_pipeline(text)[0]
        
        label = result['label']
        score = result['score']
        
        # Map to our labels
        if label == 'POSITIVE':
            return 'POSITIVE', score
        elif label == 'NEGATIVE':
            return 'NEGATIVE', score
        else:
            return 'NEUTRAL', 0.5
    except Exception as e:
        print(f"Error in DistilBERT analysis: {e}")
        return 'NEUTRAL', 0.5


def analyze_sentiment_vader(text):
    """Analyze sentiment using VADER."""
    if not text or pd.isna(text) or len(str(text).strip()) == 0:
        return 'NEUTRAL', 0.5
    
    try:
        scores = vader_analyzer.polarity_scores(str(text))
        compound = scores['compound']
        
        # Map compound score to label
        if compound >= 0.05:
            label = 'POSITIVE'
            score = compound
        elif compound <= -0.05:
            label = 'NEGATIVE'
            score = abs(compound)
        else:
            label = 'NEUTRAL'
            score = 0.5
        
        return label, score
    except Exception as e:
        print(f"Error in VADER analysis: {e}")
        return 'NEUTRAL', 0.5


def analyze_sentiment(text):
    """Analyze sentiment using the available method."""
    if USE_DISTILBERT and sentiment_pipeline:
        return analyze_sentiment_distilbert(text)
    else:
        return analyze_sentiment_vader(text)


def perform_sentiment_analysis(df):
    """Perform sentiment analysis on all reviews."""
    print("\nPerforming sentiment analysis...")
    
    # Initialize analyzer
    initialize_sentiment_analyzer()
    
    # Analyze each review
    results = []
    total = len(df)
    
    for idx, row in df.iterrows():
        if (idx + 1) % 100 == 0:
            print(f"  Processed {idx + 1}/{total} reviews...")
        
        review_text = row['review']
        sentiment_label, sentiment_score = analyze_sentiment(review_text)
        
        results.append({
            'review_id': idx,
            'sentiment_label': sentiment_label,
            'sentiment_score': sentiment_score
        })
    
    # Merge results
    sentiment_df = pd.DataFrame(results)
    df = df.reset_index(drop=True)
    df = pd.concat([df, sentiment_df[['sentiment_label', 'sentiment_score']]], axis=1)
    
    print(f"✓ Completed sentiment analysis for {len(df)} reviews")
    
    # Print summary
    print("\nSentiment Distribution:")
    sentiment_counts = df['sentiment_label'].value_counts()
    for label, count in sentiment_counts.items():
        pct = (count / len(df)) * 100
        print(f"  {label}: {count} ({pct:.1f}%)")
    
    return df


def aggregate_sentiment_by_bank(df):
    """Aggregate sentiment statistics by bank."""
    print("\nAggregating sentiment by bank...")
    
    aggregation = {
        'sentiment_score': ['mean', 'std'],
        'rating': 'mean',
        'review': 'count'
    }
    
    bank_sentiment = df.groupby('bank').agg({
        'sentiment_score': ['mean', 'std'],
        'rating': 'mean',
        'review': 'count'
    }).round(3)
    
    bank_sentiment.columns = ['avg_sentiment', 'std_sentiment', 'avg_rating', 'review_count']
    
    print("\nSentiment by Bank:")
    print(bank_sentiment)
    
    return bank_sentiment


def aggregate_sentiment_by_rating(df):
    """Aggregate sentiment statistics by rating."""
    print("\nAggregating sentiment by rating...")
    
    rating_sentiment = df.groupby('rating').agg({
        'sentiment_score': ['mean', 'std'],
        'review': 'count'
    }).round(3)
    
    rating_sentiment.columns = ['avg_sentiment', 'std_sentiment', 'review_count']
    
    print("\nSentiment by Rating:")
    print(rating_sentiment)
    
    return rating_sentiment


def main():
    """Main sentiment analysis function."""
    print("=" * 60)
    print("Sentiment Analysis")
    print("=" * 60)
    
    # Load processed data
    input_file = PROCESSED_DATA_DIR / 'reviews_processed.csv'
    if not input_file.exists():
        print(f"Error: Processed data file not found: {input_file}")
        print("Please run preprocessing first.")
        return
    
    df = pd.read_csv(input_file)
    print(f"\nLoaded {len(df)} reviews")
    
    # Perform sentiment analysis
    df = perform_sentiment_analysis(df)
    
    # Aggregate statistics
    bank_sentiment = aggregate_sentiment_by_bank(df)
    rating_sentiment = aggregate_sentiment_by_rating(df)
    
    # Save results
    output_file = ANALYSIS_DATA_DIR / 'reviews_with_sentiment.csv'
    df.to_csv(output_file, index=False, encoding='utf-8')
    print(f"\n✓ Saved results to {output_file}")
    
    # Save aggregated statistics
    bank_output = ANALYSIS_DATA_DIR / 'sentiment_by_bank.csv'
    bank_sentiment.to_csv(bank_output)
    print(f"✓ Saved bank sentiment aggregation to {bank_output}")
    
    rating_output = ANALYSIS_DATA_DIR / 'sentiment_by_rating.csv'
    rating_sentiment.to_csv(rating_output)
    print(f"✓ Saved rating sentiment aggregation to {rating_output}")
    
    # Check KPI
    analyzed_count = len(df[df['sentiment_label'].notna()])
    coverage = (analyzed_count / len(df)) * 100
    print(f"\nSentiment Analysis Coverage: {coverage:.1f}%")
    
    if coverage >= 90:
        print("✓ Meets KPI (90%+ coverage)")
    else:
        print("⚠ Does not meet KPI (90%+ coverage)")


if __name__ == '__main__':
    main()

