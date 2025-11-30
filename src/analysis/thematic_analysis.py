"""
Thematic analysis script for bank reviews.
Extracts keywords and clusters them into themes.
"""

import pandas as pd
import numpy as np
from pathlib import Path
import re
from collections import Counter
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import LatentDirichletAllocation, NMF
import spacy
import warnings
warnings.filterwarnings('ignore')

PROCESSED_DATA_DIR = Path(__file__).parent.parent.parent / 'data' / 'processed'
ANALYSIS_DATA_DIR = Path(__file__).parent.parent.parent / 'data' / 'processed'
ANALYSIS_DATA_DIR.mkdir(parents=True, exist_ok=True)

# Initialize spaCy (will load model if available)
nlp = None
try:
    nlp = spacy.load("en_core_web_sm")
    print("✓ spaCy model loaded")
except:
    print("⚠ spaCy model not found. Install with: python -m spacy download en_core_web_sm")
    print("  Continuing with basic text processing...")


def preprocess_text(text):
    """Preprocess text for keyword extraction."""
    if pd.isna(text):
        return ''
    
    text = str(text).lower()
    
    # Remove special characters but keep spaces
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text


def extract_keywords_tfidf(df, max_features=50):
    """Extract keywords using TF-IDF."""
    print("\nExtracting keywords using TF-IDF...")
    
    # Preprocess texts
    texts = [preprocess_text(text) for text in df['review']]
    
    # Create TF-IDF vectorizer
    vectorizer = TfidfVectorizer(
        max_features=max_features,
        stop_words='english',
        ngram_range=(1, 2),  # Include unigrams and bigrams
        min_df=2  # Word must appear in at least 2 documents
    )
    
    try:
        tfidf_matrix = vectorizer.fit_transform(texts)
        feature_names = vectorizer.get_feature_names_out()
        
        # Get top keywords per review
        keywords_list = []
        for i, text in enumerate(texts):
            if text.strip():
                # Get top keywords for this review
                scores = tfidf_matrix[i].toarray()[0]
                top_indices = scores.argsort()[-10:][::-1]  # Top 10 keywords
                keywords = [feature_names[idx] for idx in top_indices if scores[idx] > 0]
                keywords_list.append(', '.join(keywords[:5]))  # Top 5 per review
            else:
                keywords_list.append('')
        
        print(f"✓ Extracted keywords for {len(keywords_list)} reviews")
        return keywords_list, feature_names
    except Exception as e:
        print(f"Error in TF-IDF extraction: {e}")
        return ['' for _ in texts], []


def extract_keywords_spacy(df):
    """Extract keywords using spaCy."""
    if nlp is None:
        return None
    
    print("\nExtracting keywords using spaCy...")
    
    keywords_list = []
    
    for text in df['review']:
        if pd.isna(text) or len(str(text).strip()) == 0:
            keywords_list.append('')
            continue
        
        doc = nlp(str(text))
        
        # Extract nouns, adjectives, and important verbs
        keywords = []
        for token in doc:
            if (token.pos_ in ['NOUN', 'ADJ', 'VERB'] and 
                not token.is_stop and 
                not token.is_punct and
                len(token.text) > 2):
                keywords.append(token.lemma_.lower())
        
        keywords_list.append(', '.join(keywords[:10]))  # Top 10 per review
    
    print(f"✓ Extracted keywords using spaCy for {len(keywords_list)} reviews")
    return keywords_list


def identify_themes_manual(keywords_list, df):
    """
    Manually identify themes by grouping related keywords.
    This is a rule-based approach that groups keywords into themes.
    """
    print("\nIdentifying themes using manual clustering...")
    
    # Define theme patterns (keywords that indicate specific themes)
    theme_patterns = {
        'Account Access Issues': [
            'login', 'password', 'access', 'account', 'sign', 'authentication',
            'verify', 'security', 'locked', 'blocked'
        ],
        'Transaction Performance': [
            'transfer', 'transaction', 'payment', 'slow', 'fast', 'speed',
            'timeout', 'delay', 'processing', 'complete', 'failed'
        ],
        'User Interface & Experience': [
            'ui', 'interface', 'design', 'layout', 'navigation', 'button',
            'screen', 'display', 'user', 'experience', 'ux', 'easy', 'simple'
        ],
        'Customer Support': [
            'support', 'help', 'service', 'customer', 'contact', 'response',
            'assistance', 'issue', 'problem', 'complaint', 'resolve'
        ],
        'App Reliability': [
            'crash', 'error', 'bug', 'glitch', 'freeze', 'hang', 'close',
            'restart', 'unstable', 'reliable', 'stable', 'working'
        ],
        'Feature Requests': [
            'feature', 'add', 'want', 'need', 'missing', 'request', 'suggest',
            'improve', 'enhance', 'option', 'functionality'
        ],
        'Security & Privacy': [
            'security', 'privacy', 'safe', 'secure', 'protection', 'data',
            'personal', 'information', 'trust', 'fraud'
        ]
    }
    
    # Assign themes to each review
    review_themes = []
    
    for idx, keywords in enumerate(keywords_list):
        if not keywords:
            review_themes.append('')
            continue
        
        # Check which themes match
        matched_themes = []
        keyword_lower = keywords.lower()
        
        for theme, patterns in theme_patterns.items():
            for pattern in patterns:
                if pattern in keyword_lower:
                    matched_themes.append(theme)
                    break
        
        # Assign primary theme (first match) or 'Other' if no match
        if matched_themes:
            review_themes.append(matched_themes[0])  # Primary theme
        else:
            review_themes.append('Other')
    
    print(f"✓ Assigned themes to {len(review_themes)} reviews")
    
    # Print theme distribution
    theme_counts = Counter(review_themes)
    print("\nTheme Distribution:")
    for theme, count in theme_counts.most_common():
        pct = (count / len(review_themes)) * 100 if review_themes else 0
        print(f"  {theme}: {count} ({pct:.1f}%)")
    
    return review_themes


def identify_themes_by_bank(df, keywords_list):
    """Identify themes separately for each bank."""
    print("\nIdentifying themes by bank...")
    
    banks = df['bank'].unique()
    bank_themes = {}
    
    for bank in banks:
        bank_df = df[df['bank'] == bank].copy()
        bank_indices = bank_df.index
        bank_keywords = [keywords_list[i] for i in bank_indices]
        
        # Create temporary dataframe for this bank
        temp_df = pd.DataFrame({'review': bank_df['review'].values})
        themes = identify_themes_manual(bank_keywords, temp_df)
        
        bank_themes[bank] = themes
        
        print(f"\n{bank} Themes:")
        theme_counts = Counter(themes)
        for theme, count in theme_counts.most_common(5):
            print(f"  {theme}: {count}")
    
    return bank_themes


def main():
    """Main thematic analysis function."""
    print("=" * 60)
    print("Thematic Analysis")
    print("=" * 60)
    
    # Load data with sentiment
    input_file = ANALYSIS_DATA_DIR / 'reviews_with_sentiment.csv'
    if not input_file.exists():
        # Try processed data if sentiment file doesn't exist
        input_file = PROCESSED_DATA_DIR / 'reviews_processed.csv'
        if not input_file.exists():
            print(f"Error: Data file not found")
            print("Please run preprocessing and sentiment analysis first.")
            return
    
    df = pd.read_csv(input_file)
    print(f"\nLoaded {len(df)} reviews")
    
    # Extract keywords
    keywords_list, feature_names = extract_keywords_tfidf(df)
    df['keywords'] = keywords_list
    
    # Identify themes
    themes = identify_themes_manual(keywords_list, df)
    df['theme'] = themes
    
    # Identify themes by bank
    bank_themes = identify_themes_by_bank(df, keywords_list)
    
    # Save results
    output_file = ANALYSIS_DATA_DIR / 'reviews_with_themes.csv'
    df.to_csv(output_file, index=False, encoding='utf-8')
    print(f"\n✓ Saved results to {output_file}")
    
    # Save theme summary by bank
    theme_summary = []
    for bank, themes_list in bank_themes.items():
        theme_counts = Counter(themes_list)
        for theme, count in theme_counts.most_common(5):
            theme_summary.append({
                'bank': bank,
                'theme': theme,
                'count': count,
                'percentage': (count / len(themes_list)) * 100
            })
    
    theme_summary_df = pd.DataFrame(theme_summary)
    theme_output = ANALYSIS_DATA_DIR / 'themes_by_bank.csv'
    theme_summary_df.to_csv(theme_output, index=False)
    print(f"✓ Saved theme summary to {theme_output}")
    
    # Check KPI
    banks = df['bank'].unique()
    print(f"\nTheme Coverage:")
    for bank in banks:
        bank_df = df[df['bank'] == bank]
        unique_themes = bank_df['theme'].nunique()
        print(f"  {bank}: {unique_themes} themes")
        
        if unique_themes >= 3:
            print(f"    ✓ Meets KPI (3+ themes)")
        else:
            print(f"    ⚠ Does not meet KPI (3+ themes)")


if __name__ == '__main__':
    main()

