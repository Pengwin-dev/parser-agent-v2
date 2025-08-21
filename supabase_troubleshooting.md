# Supabase SQL Troubleshooting Guide

## 🚨 **Common SQL Errors & Solutions**

### **Error 1: "Permission denied" or "Insufficient privileges"**
**Solution:**
- Make sure you're logged into Supabase with the correct account
- Check if you have admin/owner access to the project
- Try running SQL as the `postgres` user (default admin)

### **Error 2: "Table already exists"**
**Solution:**
- Use `CREATE TABLE IF NOT EXISTS` (already in our script)
- Or drop the table first: `DROP TABLE IF EXISTS pitch_decks;`

### **Error 3: "Function already exists"**
**Solution:**
- Use `CREATE OR REPLACE FUNCTION` (already in our script)
- Or drop the function first: `DROP FUNCTION IF EXISTS update_updated_at_column();`

### **Error 4: "Trigger already exists"**
**Solution:**
- Drop the trigger first: `DROP TRIGGER IF EXISTS update_pitch_decks_updated_at ON pitch_decks;`

## 🔧 **Step-by-Step Execution**

### **Option 1: Run Everything at Once**
Copy the entire `supabase_table.sql` file and paste it into Supabase SQL Editor, then click **Run**.

### **Option 2: Run Step by Step (Recommended for troubleshooting)**

#### **Step 1: Create Basic Table**
```sql
CREATE TABLE IF NOT EXISTS pitch_decks (
    id UUID PRIMARY KEY,
    pitch_deck_link TEXT NOT NULL,
    funds_list_link TEXT NOT NULL,
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
```

#### **Step 2: Add Advanced Features**
```sql
-- Add workflow_type column if not exists
ALTER TABLE pitch_decks ADD COLUMN IF NOT EXISTS workflow_type TEXT DEFAULT 'pitch_deck';

-- Add original_filename column if not exists
ALTER TABLE pitch_decks ADD COLUMN IF NOT EXISTS original_filename TEXT;
```

#### **Step 3: Create Indexes**
```sql
CREATE INDEX IF NOT EXISTS idx_pitch_decks_company_name ON pitch_decks(company_name);
CREATE INDEX IF NOT EXISTS idx_pitch_decks_created_at ON pitch_decks(created_at);
```

#### **Step 4: Test with Sample Data**
```sql
INSERT INTO pitch_decks (
    id, 
    pitch_deck_link, 
    funds_list_link, 
    company_name, 
    description
) VALUES (
    gen_random_uuid(),
    'https://example.com/test.pdf',
    'https://example.com/test.csv',
    'Test Company',
    'Test Description'
);
```

#### **Step 5: Verify Everything Works**
```sql
SELECT COUNT(*) FROM pitch_decks;
SELECT * FROM pitch_decks LIMIT 1;
```

## 🎯 **Alternative: Use Supabase Dashboard**

If SQL continues to give errors, you can create the table through the Supabase dashboard:

1. **Go to Table Editor** in your Supabase project
2. **Click "New Table"**
3. **Set table name**: `pitch_decks`
4. **Add columns manually**:
   - `id` (type: `uuid`, primary key, default: `gen_random_uuid()`)
   - `pitch_deck_link` (type: `text`, not null)
   - `funds_list_link` (type: `text`, not null)
   - `company_name` (type: `text`)
   - `description` (type: `text`)
   - `problem` (type: `text`)
   - `solution` (type: `text`)
   - `funding_info` (type: `text`)
   - `industry_sectors` (type: `text`)
   - `pages_processed` (type: `int8`, default: `0`)
   - `text_extracted_chars` (type: `int8`, default: `0`)
   - `total_funds` (type: `int8`, default: `0`)
   - `funds_data` (type: `jsonb`)
   - `extracted_at` (type: `timestamptz`, default: `now()`)
   - `raw_summary` (type: `jsonb`)
   - `status` (type: `text`, default: `'completed'`)
   - `created_at` (type: `timestamptz`, default: `now()`)
   - `updated_at` (type: `timestamptz`, default: `now()`)

## 🔍 **Debug Commands**

Run these in Supabase SQL Editor to check your setup:

```sql
-- Check if table exists
SELECT table_name FROM information_schema.tables WHERE table_name = 'pitch_decks';

-- Check table structure
SELECT column_name, data_type, is_nullable FROM information_schema.columns WHERE table_name = 'pitch_decks';

-- Check if you have permissions
SELECT has_table_privilege('pitch_decks', 'INSERT') as can_insert;
```

## 📞 **Still Having Issues?**

1. **Copy the exact error message** from Supabase
2. **Check your Supabase project status** (make sure it's active)
3. **Try creating a simple test table first** to verify basic permissions
4. **Contact Supabase support** if the issue persists

## ✅ **Success Indicators**

When everything works correctly, you should see:
- ✅ Table created without errors
- ✅ Sample data inserted successfully
- ✅ Queries return expected results
- ✅ No permission or syntax errors



