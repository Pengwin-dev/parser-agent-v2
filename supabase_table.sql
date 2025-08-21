-- Create the pitch_decks table in Supabase
-- Run this in your Supabase SQL editor

CREATE TABLE IF NOT EXISTS pitch_decks (
    id UUID PRIMARY KEY,
    pitch_deck_link TEXT NOT NULL,
    funds_list_link TEXT NOT NULL,
    original_filename TEXT,
    workflow_type TEXT DEFAULT 'pitch_deck',
    company_name TEXT,
    description TEXT,
    problem TEXT,
    solution TEXT,
    funding_info TEXT,
    industry_sectors TEXT,
    pages_processed INTEGER DEFAULT 0,
    text_extracted_chars INTEGER DEFAULT 0,
    total_funds INTEGER DEFAULT 0,
    funds_data JSONB,
    extracted_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    raw_summary JSONB,
    status TEXT DEFAULT 'completed',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_pitch_decks_company_name ON pitch_decks(company_name);
CREATE INDEX IF NOT EXISTS idx_pitch_decks_industry_sectors ON pitch_decks(industry_sectors);
CREATE INDEX IF NOT EXISTS idx_pitch_decks_extracted_at ON pitch_decks(extracted_at);

-- Enable Row Level Security (RLS) - optional
-- ALTER TABLE pitch_decks ENABLE ROW LEVEL SECURITY;

-- Create a policy for public access (adjust based on your security needs)
-- CREATE POLICY "Allow public access" ON pitch_decks FOR ALL USING (true);

-- Create a function to update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create a trigger to automatically update the updated_at column
CREATE TRIGGER update_pitch_decks_updated_at 
    BEFORE UPDATE ON pitch_decks 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- Insert a sample record for testing (optional)
-- INSERT INTO pitch_decks (
--     id, 
--     pitch_deck_link, 
--     funds_list_link, 
--     company_name, 
--     description
-- ) VALUES (
--     gen_random_uuid(),
--     'https://example.com/pitch-deck.pdf',
--     'https://example.com/funds-list.pdf',
--     'Sample Company',
--     'This is a sample company description'
-- );
