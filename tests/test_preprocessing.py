"""
Unit tests for preprocessing functions.
"""

import unittest
import pandas as pd
import numpy as np
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from preprocessing.preprocess_reviews import (
    remove_duplicates,
    handle_missing_data,
    normalize_dates,
    clean_review_text
)


class TestPreprocessing(unittest.TestCase):
    """Test preprocessing functions."""
    
    def setUp(self):
        """Set up test data."""
        self.test_data = pd.DataFrame({
            'review': [
                'Great app!',
                'Great app!',  # Duplicate
                'Love it',
                None,  # Missing
                '   Too many spaces   ',
                'Bad app'
            ],
            'rating': [5, 5, 4, None, 3, 1],
            'date': [
                '2024-01-01',
                '2024-01-01',
                '01/15/2024',
                '2024-01-01',
                '2024-01-01',
                '2024-01-01'
            ],
            'bank': ['CBE', 'CBE', 'BOA', 'CBE', 'Dashen', 'CBE'],
            'source': ['Google Play'] * 6
        })
    
    def test_remove_duplicates(self):
        """Test duplicate removal."""
        result = remove_duplicates(self.test_data)
        self.assertEqual(len(result), 5)  # One duplicate removed
    
    def test_handle_missing_data(self):
        """Test missing data handling."""
        result = handle_missing_data(self.test_data)
        # Should remove rows with missing review or invalid rating
        self.assertGreater(len(result), 0)
        self.assertFalse(result['review'].isna().any())
    
    def test_normalize_dates(self):
        """Test date normalization."""
        result = normalize_dates(self.test_data)
        # All dates should be in YYYY-MM-DD format
        for date in result['date']:
            self.assertRegex(str(date), r'\d{4}-\d{2}-\d{2}')
    
    def test_clean_review_text(self):
        """Test text cleaning."""
        result = clean_review_text(self.test_data)
        # Check that extra spaces are removed
        self.assertNotIn('   ', result['review'].values)


if __name__ == '__main__':
    unittest.main()

