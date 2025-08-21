# Supabase Integration Setup Guide

This guide will help you set up Supabase integration with your PDF Parser API to store extracted pitch deck data.

## 🚀 **Prerequisites**

1. **Supabase Account**: Sign up at [supabase.com](https://supabase.com)
2. **Python Dependencies**: Install the new requirements
3. **Environment Variables**: Configure your Supabase credentials

## 📦 **Installation**

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Create Environment File
Create a `.env` file in your project root:
```env
# Supabase Configuration
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your_supabase_anon_key

# Optional: Custom table name
SUPABASE_TABLE=pitch_decks

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
```

## 🗄️ **Database Setup**

### 1. Create Table in Supabase
1. Go to your Supabase project dashboard
2. Navigate to **SQL Editor**
3. Copy and paste the contents of `supabase_table.sql`
4. Click **Run** to execute the script

### 2. Table Structure
The `pitch_decks` table will have these columns:
- `id` (UUID, Primary Key)
- `pitch_deck_link` (Text, Required)
- `funds_list_link` (Text, Required)
- `company_name`, `description`, `problem`, `solution`
- `funding_info`, `industry_sectors`
- `pages_processed`, `text_extracted_chars`
- `extracted_at`, `raw_summary` (JSON)
- `created_at`, `updated_at` (Timestamps)

## 🔧 **Configuration**

### 1. Get Supabase Credentials
1. Go to your Supabase project dashboard
2. Navigate to **Settings** → **API**
3. Copy:
   - **Project URL** → `SUPABASE_URL`
   - **anon public** key → `SUPABASE_KEY`

### 2. Update Environment File
Replace the placeholder values in your `.env` file:
```env
SUPABASE_URL=https://abcdefghijklmnop.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

## 🧪 **Testing the Integration**

### 1. Test Supabase Connection
```bash
python test_supabase.py
```

### 2. Manual API Testing
Use Postman or curl to test the new endpoints:

#### **Health Check**
```bash
curl http://localhost:8000/health/supabase
```

#### **Store Pitch Deck Data**
```bash
curl -X POST "http://localhost:8000/store-pitch-deck" \
  -H "Content-Type: application/json" \
  -d '{
    "pitch_deck_link": "https://example.com/pitch-deck.pdf",
    "funds_list_link": "https://example.com/funds-list.pdf",
    "file_id": "your-file-id-here"
  }'
```

## 📱 **New API Endpoints**

### 1. **GET /health/supabase**
Check Supabase connection health.

### 2. **POST /store-pitch-deck**
Store extracted pitch deck data with links.

**Request Body:**
```json
{
  "pitch_deck_link": "https://example.com/pitch-deck.pdf",
  "funds_list_link": "https://example.com/funds-list.pdf",
  "file_id": "uuid-string"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Pitch deck data stored successfully",
  "file_id": "uuid-string",
  "stored_data": { ... }
}
```

### 3. **GET /pitch-decks/{file_id}**
Retrieve stored pitch deck data by ID.

### 4. **GET /pitch-decks**
Retrieve all pitch deck records (with optional limit).

## 🔄 **Complete Workflow**

### 1. **Upload PDF**
```bash
POST /upload-pdf
# Returns: file_id, summary data
```

### 2. **Store with Links**
```bash
POST /store-pitch-deck
# Body: pitch_deck_link, funds_list_link, file_id
# Stores: extracted data + links in Supabase
```

### 3. **Retrieve Data**
```bash
GET /pitch-decks/{file_id}
# Returns: complete stored record
```

## 🎯 **n8n Integration**

### **Workflow Steps:**
1. **File Trigger** → PDF detected
2. **HTTP Request** → `POST /upload-pdf` (extract data)
3. **HTTP Request** → `POST /store-pitch-deck` (store with links)
4. **Database** → Data stored in Supabase
5. **Next Steps** → Process stored data

### **n8n HTTP Request Configuration:**

#### **Store Pitch Deck Node**
- **Method**: POST
- **URL**: `http://localhost:8000/store-pitch-deck`
- **Body**: JSON
```json
{
  "pitch_deck_link": "{{$json.pitch_deck_url}}",
  "funds_list_link": "{{$json.funds_list_url}}",
  "file_id": "{{$json.file_id}}"
}
```

## 🚨 **Troubleshooting**

### **Common Issues:**

1. **"Supabase connection failed"**
   - Check `SUPABASE_URL` and `SUPABASE_KEY`
   - Verify your Supabase project is active
   - Check if the table exists

2. **"Table not found"**
   - Run the SQL script in Supabase SQL Editor
   - Check table name in your `.env` file

3. **"Permission denied"**
   - Check Row Level Security (RLS) settings
   - Verify your API key has proper permissions

### **Debug Steps:**
1. Test connection: `GET /health/supabase`
2. Check environment variables
3. Verify table exists in Supabase
4. Check API logs for detailed errors

## 🔐 **Security Considerations**

### **Production Setup:**
1. **Environment Variables**: Never commit `.env` files
2. **API Keys**: Use service role keys for admin operations
3. **RLS Policies**: Implement proper access control
4. **HTTPS**: Use HTTPS in production

### **RLS Policy Example:**
```sql
-- Enable RLS
ALTER TABLE pitch_decks ENABLE ROW LEVEL SECURITY;

-- Create policy for authenticated users
CREATE POLICY "Users can view their own pitch decks" 
ON pitch_decks FOR SELECT 
USING (auth.uid() = user_id);
```

## 📊 **Data Flow**

```
PDF Upload → Text Extraction → Summary Generation → Store in Supabase
     ↓              ↓                ↓                ↓
  File ID    Structured Data   Business Info    Database Record
     ↓              ↓                ↓                ↓
  Links +    Company, Problem,  Funding,        Queryable
  Metadata   Solution, etc.     Industries      Data
```

## 🎉 **Ready to Use!**

Your PDF Parser API is now fully integrated with Supabase and ready to:
- ✅ Extract business information from PDFs
- ✅ Store structured data with links
- ✅ Query and retrieve stored records
- ✅ Integrate with n8n workflows
- ✅ Scale with your business needs

Start by testing the connection and then integrate it into your automation workflows! 🚀

