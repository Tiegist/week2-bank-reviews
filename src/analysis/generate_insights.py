"""
Generate insights and recommendations from analyzed review data.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from collections import Counter

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
        return pd.read_csv(input_file)
    return None


def identify_drivers_and_pain_points(df, bank_name=None):
    """Identify satisfaction drivers and pain points for a bank."""
    if bank_name:
        bank_df = df[df['bank'] == bank_name].copy()
        title = f"{bank_name}"
    else:
        bank_df = df.copy()
        title = "Overall"
    
    insights = {
        'drivers': [],
        'pain_points': []
    }
    
    # Analyze by sentiment and theme
    if 'sentiment_label' in bank_df.columns and 'theme' in bank_df.columns:
        # Drivers: Positive sentiment themes
        positive_reviews = bank_df[bank_df['sentiment_label'] == 'POSITIVE']
        if len(positive_reviews) > 0:
            top_positive_themes = positive_reviews['theme'].value_counts().head(3)
            for theme, count in top_positive_themes.items():
                if theme and theme != 'Other':
                    pct = (count / len(positive_reviews)) * 100
                    insights['drivers'].append({
                        'theme': theme,
                        'count': count,
                        'percentage': pct
                    })
        
        # Pain points: Negative sentiment themes
        negative_reviews = bank_df[bank_df['sentiment_label'] == 'NEGATIVE']
        if len(negative_reviews) > 0:
            top_negative_themes = negative_reviews['theme'].value_counts().head(3)
            for theme, count in top_negative_themes.items():
                if theme and theme != 'Other':
                    pct = (count / len(negative_reviews)) * 100
                    insights['pain_points'].append({
                        'theme': theme,
                        'count': count,
                        'percentage': pct
                    })
    
    # Analyze by rating
    if 'rating' in bank_df.columns:
        # Low ratings (1-2 stars) indicate pain points
        low_ratings = bank_df[bank_df['rating'] <= 2]
        if len(low_ratings) > 0 and 'theme' in low_ratings.columns:
            low_rating_themes = low_ratings['theme'].value_counts().head(2)
            for theme, count in low_rating_themes.items():
                if theme and theme != 'Other':
                    # Check if not already in pain points
                    if not any(p['theme'] == theme for p in insights['pain_points']):
                        insights['pain_points'].append({
                            'theme': theme,
                            'count': count,
                            'percentage': (count / len(low_ratings)) * 100
                        })
        
        # High ratings (4-5 stars) indicate drivers
        high_ratings = bank_df[bank_df['rating'] >= 4]
        if len(high_ratings) > 0 and 'theme' in high_ratings.columns:
            high_rating_themes = high_ratings['theme'].value_counts().head(2)
            for theme, count in high_rating_themes.items():
                if theme and theme != 'Other':
                    # Check if not already in drivers
                    if not any(d['theme'] == theme for d in insights['drivers']):
                        insights['drivers'].append({
                            'theme': theme,
                            'count': count,
                            'percentage': (count / len(high_ratings)) * 100
                        })
    
    return insights


def generate_recommendations(df, bank_name):
    """Generate recommendations for a bank."""
    insights = identify_drivers_and_pain_points(df, bank_name)
    recommendations = []
    
    # Recommendations based on pain points
    for pain_point in insights['pain_points']:
        theme = pain_point['theme']
        
        if 'Account Access' in theme:
            recommendations.append({
                'category': 'Account Access',
                'recommendation': 'Improve login process and authentication mechanisms. Consider implementing biometric authentication and password recovery options.',
                'priority': 'High'
            })
        elif 'Transaction Performance' in theme:
            recommendations.append({
                'category': 'Performance',
                'recommendation': 'Optimize transaction processing speed. Investigate server response times and implement caching strategies.',
                'priority': 'High'
            })
        elif 'User Interface' in theme or 'Experience' in theme:
            recommendations.append({
                'category': 'UX/UI',
                'recommendation': 'Redesign user interface for better usability. Conduct user testing and implement modern design patterns.',
                'priority': 'Medium'
            })
        elif 'Customer Support' in theme:
            recommendations.append({
                'category': 'Support',
                'recommendation': 'Enhance customer support channels. Consider implementing AI chatbot for faster response times.',
                'priority': 'High'
            })
        elif 'Reliability' in theme:
            recommendations.append({
                'category': 'Stability',
                'recommendation': 'Fix app crashes and stability issues. Implement comprehensive error handling and testing.',
                'priority': 'Critical'
            })
    
    # Feature recommendations based on drivers
    for driver in insights['drivers']:
        theme = driver['theme']
        if 'Transaction Performance' in theme:
            recommendations.append({
                'category': 'Enhancement',
                'recommendation': 'Leverage fast transaction processing as a competitive advantage. Market this feature prominently.',
                'priority': 'Low'
            })
    
    return recommendations


def compare_banks(df):
    """Compare banks and identify competitive advantages."""
    banks = df['bank'].unique()
    comparison = {}
    
    for bank in banks:
        bank_df = df[df['bank'] == bank]
        
        comparison[bank] = {
            'avg_rating': bank_df['rating'].mean() if 'rating' in bank_df.columns else 0,
            'total_reviews': len(bank_df),
            'positive_pct': (len(bank_df[bank_df['sentiment_label'] == 'POSITIVE']) / len(bank_df) * 100) 
                           if 'sentiment_label' in bank_df.columns else 0,
            'negative_pct': (len(bank_df[bank_df['sentiment_label'] == 'NEGATIVE']) / len(bank_df) * 100) 
                          if 'sentiment_label' in bank_df.columns else 0,
        }
    
    return comparison


def generate_insights_report():
    """Generate comprehensive insights report."""
    print("=" * 60)
    print("Generating Insights and Recommendations")
    print("=" * 60)
    
    df = load_data()
    if df is None:
        print("Error: No data found")
        return
    
    banks = df['bank'].unique()
    
    report = []
    report.append("# Bank Review Analysis - Insights and Recommendations\n")
    report.append("=" * 60 + "\n\n")
    
    # Overall summary
    report.append("## Executive Summary\n\n")
    report.append(f"Total Reviews Analyzed: {len(df)}\n")
    report.append(f"Banks Analyzed: {', '.join(banks)}\n\n")
    
    if 'sentiment_label' in df.columns:
        sentiment_dist = df['sentiment_label'].value_counts()
        report.append("Overall Sentiment Distribution:\n")
        for label, count in sentiment_dist.items():
            pct = (count / len(df)) * 100
            report.append(f"- {label}: {count} ({pct:.1f}%)\n")
        report.append("\n")
    
    # Bank comparison
    report.append("## Bank Comparison\n\n")
    comparison = compare_banks(df)
    
    comparison_df = pd.DataFrame(comparison).T
    report.append(comparison_df.to_string())
    report.append("\n\n")
    
    # Insights per bank
    for bank in banks:
        report.append(f"## {bank}\n\n")
        
        # Drivers and pain points
        insights = identify_drivers_and_pain_points(df, bank)
        
        report.append("### Satisfaction Drivers\n\n")
        if insights['drivers']:
            for driver in insights['drivers'][:3]:
                report.append(f"- **{driver['theme']}**: {driver['count']} mentions ({driver['percentage']:.1f}% of positive reviews)\n")
        else:
            report.append("- No clear drivers identified\n")
        report.append("\n")
        
        report.append("### Pain Points\n\n")
        if insights['pain_points']:
            for pain_point in insights['pain_points'][:3]:
                report.append(f"- **{pain_point['theme']}**: {pain_point['count']} mentions ({pain_point['percentage']:.1f}% of negative reviews)\n")
        else:
            report.append("- No clear pain points identified\n")
        report.append("\n")
        
        # Recommendations
        recommendations = generate_recommendations(df, bank)
        report.append("### Recommendations\n\n")
        if recommendations:
            for rec in recommendations[:3]:
                report.append(f"- **[{rec['priority']} Priority] {rec['category']}**: {rec['recommendation']}\n")
        else:
            report.append("- Continue monitoring user feedback\n")
        report.append("\n")
    
    # Save report
    report_text = ''.join(report)
    output_file = REPORTS_DIR / 'insights_report.md'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(report_text)
    
    print(f"✓ Insights report saved to {output_file}")
    
    # Also save as structured data
    insights_data = {}
    for bank in banks:
        insights_data[bank] = {
            'insights': identify_drivers_and_pain_points(df, bank),
            'recommendations': generate_recommendations(df, bank)
        }
    
    import json
    insights_json = REPORTS_DIR / 'insights_data.json'
    with open(insights_json, 'w', encoding='utf-8') as f:
        json.dump(insights_data, f, indent=2, ensure_ascii=False)
    
    print(f"✓ Insights data saved to {insights_json}")
    
    return insights_data


if __name__ == '__main__':
    generate_insights_report()

