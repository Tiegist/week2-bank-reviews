-- PostgreSQL Database Schema for Bank Reviews
-- Database: bank_reviews

-- Drop tables if they exist (for clean setup)
DROP TABLE IF EXISTS reviews CASCADE;
DROP TABLE IF EXISTS banks CASCADE;

-- Banks Table
CREATE TABLE banks (
    bank_id SERIAL PRIMARY KEY,
    bank_name VARCHAR(255) NOT NULL UNIQUE,
    app_name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Reviews Table
CREATE TABLE reviews (
    review_id SERIAL PRIMARY KEY,
    bank_id INTEGER NOT NULL REFERENCES banks(bank_id) ON DELETE CASCADE,
    review_text TEXT NOT NULL,
    rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
    review_date DATE NOT NULL,
    sentiment_label VARCHAR(20),
    sentiment_score DECIMAL(5, 3),
    theme VARCHAR(255),
    keywords TEXT,
    source VARCHAR(100) DEFAULT 'Google Play Store',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better query performance
CREATE INDEX idx_reviews_bank_id ON reviews(bank_id);
CREATE INDEX idx_reviews_rating ON reviews(rating);
CREATE INDEX idx_reviews_sentiment ON reviews(sentiment_label);
CREATE INDEX idx_reviews_theme ON reviews(theme);
CREATE INDEX idx_reviews_date ON reviews(review_date);

-- Insert bank data
INSERT INTO banks (bank_name, app_name) VALUES
    ('Commercial Bank of Ethiopia', 'Commercial Bank of Ethiopia Mobile'),
    ('Bank of Abyssinia', 'Bank of Abyssinia Mobile'),
    ('Dashen Bank', 'Dashen Bank Mobile')
ON CONFLICT (bank_name) DO NOTHING;

-- Verification queries
SELECT 'Banks table created successfully' AS status;
SELECT 'Reviews table created successfully' AS status;
SELECT COUNT(*) AS bank_count FROM banks;
SELECT COUNT(*) AS review_count FROM reviews;

