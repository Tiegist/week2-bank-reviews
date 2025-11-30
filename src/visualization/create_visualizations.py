"""
Create visualizations for bank review analysis.
Generates plots for sentiment trends, rating distributions, keyword clouds, etc.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from wordcloud import WordCloud
import warnings
warnings.filterwarnings('ignore')

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 6)
plt.rcParams['font.size'] = 10

ANALYSIS_DATA_DIR = Path(__file__).parent.parent.parent / 'data' / 'processed'
REPORTS_DIR = Path(__file__).parent.parent.parent / 'reports'
REPORTS_DIR.mkdir(parents=True, exist_ok=True)


def load_data():
    """Load processed review data."""
    input_file = ANALYSIS_DATA_DIR / 'reviews_with_themes.csv'
    
    if not input_file.exists():
        input_file = ANALYSIS_DATA_DIR / 'reviews_with_sentiment.csv'
        if not input_file.exists():
            input_file = ANALYSIS_DATA_DIR / 'reviews_processed.csv'
    
    if input_file.exists():
        df = pd.read_csv(input_file)
        print(f"Loaded {len(df)} reviews")
        return df
    else:
        print("Error: No data file found")
        return None


def plot_sentiment_distribution(df):
    """Plot sentiment distribution by bank."""
    print("Creating sentiment distribution plot...")
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    
    # Overall sentiment distribution
    sentiment_counts = df['sentiment_label'].value_counts()
    axes[0].bar(sentiment_counts.index, sentiment_counts.values, 
                color=['#2ecc71', '#e74c3c', '#95a5a6'])
    axes[0].set_title('Overall Sentiment Distribution', fontsize=14, fontweight='bold')
    axes[0].set_xlabel('Sentiment')
    axes[0].set_ylabel('Number of Reviews')
    axes[0].grid(axis='y', alpha=0.3)
    
    # Sentiment by bank
    if 'bank' in df.columns:
        sentiment_by_bank = pd.crosstab(df['bank'], df['sentiment_label'])
        sentiment_by_bank.plot(kind='bar', ax=axes[1], color=['#2ecc71', '#e74c3c', '#95a5a6'])
        axes[1].set_title('Sentiment Distribution by Bank', fontsize=14, fontweight='bold')
        axes[1].set_xlabel('Bank')
        axes[1].set_ylabel('Number of Reviews')
        axes[1].legend(title='Sentiment')
        axes[1].tick_params(axis='x', rotation=45)
        axes[1].grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    output_file = REPORTS_DIR / 'sentiment_distribution.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"  Saved to {output_file}")
    plt.close()


def plot_rating_distribution(df):
    """Plot rating distribution."""
    print("Creating rating distribution plot...")
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    
    # Overall rating distribution
    rating_counts = df['rating'].value_counts().sort_index()
    axes[0].bar(rating_counts.index, rating_counts.values, color='#3498db')
    axes[0].set_title('Overall Rating Distribution', fontsize=14, fontweight='bold')
    axes[0].set_xlabel('Rating (Stars)')
    axes[0].set_ylabel('Number of Reviews')
    axes[0].set_xticks(range(1, 6))
    axes[0].grid(axis='y', alpha=0.3)
    
    # Rating by bank
    if 'bank' in df.columns:
        rating_by_bank = pd.crosstab(df['bank'], df['rating'])
        rating_by_bank.plot(kind='bar', ax=axes[1], color=['#e74c3c', '#f39c12', '#f1c40f', '#2ecc71', '#27ae60'])
        axes[1].set_title('Rating Distribution by Bank', fontsize=14, fontweight='bold')
        axes[1].set_xlabel('Bank')
        axes[1].set_ylabel('Number of Reviews')
        axes[1].legend(title='Rating', labels=['1★', '2★', '3★', '4★', '5★'])
        axes[1].tick_params(axis='x', rotation=45)
        axes[1].grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    output_file = REPORTS_DIR / 'rating_distribution.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"  Saved to {output_file}")
    plt.close()


def plot_sentiment_trends(df):
    """Plot sentiment trends over time."""
    print("Creating sentiment trends plot...")
    
    if 'date' not in df.columns:
        print("  ⚠ Date column not found, skipping trend plot")
        return
    
    # Convert date to datetime
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    df = df.dropna(subset=['date'])
    
    # Group by month
    df['month'] = df['date'].dt.to_period('M')
    monthly_sentiment = df.groupby(['month', 'sentiment_label']).size().unstack(fill_value=0)
    
    fig, ax = plt.subplots(figsize=(14, 6))
    monthly_sentiment.plot(kind='line', ax=ax, marker='o', linewidth=2)
    ax.set_title('Sentiment Trends Over Time', fontsize=14, fontweight='bold')
    ax.set_xlabel('Month')
    ax.set_ylabel('Number of Reviews')
    ax.legend(title='Sentiment')
    ax.grid(alpha=0.3)
    plt.xticks(rotation=45)
    
    plt.tight_layout()
    output_file = REPORTS_DIR / 'sentiment_trends.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"  Saved to {output_file}")
    plt.close()


def plot_theme_distribution(df):
    """Plot theme distribution."""
    print("Creating theme distribution plot...")
    
    if 'theme' not in df.columns:
        print("  ⚠ Theme column not found, skipping theme plot")
        return
    
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))
    
    # Overall theme distribution
    theme_counts = df['theme'].value_counts().head(10)
    axes[0].barh(theme_counts.index, theme_counts.values, color='#9b59b6')
    axes[0].set_title('Top 10 Themes (Overall)', fontsize=14, fontweight='bold')
    axes[0].set_xlabel('Number of Reviews')
    axes[0].grid(axis='x', alpha=0.3)
    
    # Theme by bank
    if 'bank' in df.columns:
        theme_by_bank = pd.crosstab(df['bank'], df['theme'])
        top_themes = theme_by_bank.sum().nlargest(5).index
        theme_by_bank[top_themes].plot(kind='bar', ax=axes[1], width=0.8)
        axes[1].set_title('Top Themes by Bank', fontsize=14, fontweight='bold')
        axes[1].set_xlabel('Bank')
        axes[1].set_ylabel('Number of Reviews')
        axes[1].legend(title='Theme', bbox_to_anchor=(1.05, 1), loc='upper left')
        axes[1].tick_params(axis='x', rotation=45)
        axes[1].grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    output_file = REPORTS_DIR / 'theme_distribution.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"  Saved to {output_file}")
    plt.close()


def create_wordcloud(df):
    """Create word cloud from review text."""
    print("Creating word cloud...")
    
    # Combine all review text
    all_text = ' '.join(df['review'].dropna().astype(str))
    
    if len(all_text) < 10:
        print("  ⚠ Not enough text for word cloud")
        return
    
    # Create word cloud
    wordcloud = WordCloud(
        width=1200,
        height=600,
        background_color='white',
        max_words=100,
        colormap='viridis'
    ).generate(all_text)
    
    plt.figure(figsize=(14, 7))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.title('Word Cloud of Review Text', fontsize=16, fontweight='bold', pad=20)
    
    output_file = REPORTS_DIR / 'wordcloud.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"  Saved to {output_file}")
    plt.close()


def plot_bank_comparison(df):
    """Create comparison plots between banks."""
    print("Creating bank comparison plot...")
    
    if 'bank' not in df.columns:
        print("  ⚠ Bank column not found, skipping comparison")
        return
    
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    
    # Average rating by bank
    avg_rating = df.groupby('bank')['rating'].mean().sort_values(ascending=False)
    axes[0, 0].barh(avg_rating.index, avg_rating.values, color='#3498db')
    axes[0, 0].set_title('Average Rating by Bank', fontsize=12, fontweight='bold')
    axes[0, 0].set_xlabel('Average Rating')
    axes[0, 0].grid(axis='x', alpha=0.3)
    
    # Average sentiment score by bank
    if 'sentiment_score' in df.columns:
        avg_sentiment = df.groupby('bank')['sentiment_score'].mean().sort_values(ascending=False)
        axes[0, 1].barh(avg_sentiment.index, avg_sentiment.values, color='#2ecc71')
        axes[0, 1].set_title('Average Sentiment Score by Bank', fontsize=12, fontweight='bold')
        axes[0, 1].set_xlabel('Average Sentiment Score')
        axes[0, 1].grid(axis='x', alpha=0.3)
    
    # Review count by bank
    review_count = df['bank'].value_counts()
    axes[1, 0].bar(review_count.index, review_count.values, color='#9b59b6')
    axes[1, 0].set_title('Number of Reviews by Bank', fontsize=12, fontweight='bold')
    axes[1, 0].set_xlabel('Bank')
    axes[1, 0].set_ylabel('Number of Reviews')
    axes[1, 0].tick_params(axis='x', rotation=45)
    axes[1, 0].grid(axis='y', alpha=0.3)
    
    # Positive sentiment percentage by bank
    if 'sentiment_label' in df.columns:
        positive_pct = df[df['sentiment_label'] == 'POSITIVE'].groupby('bank').size() / df.groupby('bank').size() * 100
        positive_pct = positive_pct.sort_values(ascending=False)
        axes[1, 1].barh(positive_pct.index, positive_pct.values, color='#27ae60')
        axes[1, 1].set_title('Positive Sentiment % by Bank', fontsize=12, fontweight='bold')
        axes[1, 1].set_xlabel('Percentage (%)')
        axes[1, 1].grid(axis='x', alpha=0.3)
    
    plt.tight_layout()
    output_file = REPORTS_DIR / 'bank_comparison.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"  Saved to {output_file}")
    plt.close()


def main():
    """Main visualization function."""
    print("=" * 60)
    print("Creating Visualizations")
    print("=" * 60)
    
    # Load data
    df = load_data()
    if df is None:
        return
    
    # Create visualizations
    plot_sentiment_distribution(df)
    plot_rating_distribution(df)
    plot_sentiment_trends(df)
    plot_theme_distribution(df)
    create_wordcloud(df)
    plot_bank_comparison(df)
    
    print("\n✓ All visualizations created successfully!")
    print(f"  Output directory: {REPORTS_DIR}")


if __name__ == '__main__':
    main()

