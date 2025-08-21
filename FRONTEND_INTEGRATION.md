# Frontend Integration Guide

This guide explains how your Next.js frontend integrates with the `parser-agent` backend to create a complete fundraise workflow.

## 🏗️ **Architecture Overview**

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Next.js UI    │    │  Supabase Storage│    │ Parser Backend  │
│                 │    │                  │    │                 │
│ • Upload PDF    │───▶│ • Store PDF      │    │ • Download PDF  │
│ • Upload CSV    │───▶│ • Store CSV      │    │ • Download CSV  │
│ • FUNDRAISE     │───▶│ • Get public URLs│    │ • Parse content │
│   Button        │    │                  │    │ • Store results │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## 🔄 **Complete Workflow**

### **Phase 1: File Uploads**
1. **User uploads Pitch Deck PDF**
   - Frontend uploads to Supabase storage
   - Gets public URL: `https://xxx.supabase.co/storage/v1/object/public/bucket/pitch-deck.pdf`
   - FUNDRAISE button remains **disabled**

2. **User uploads 50 Funds CSV**
   - Frontend uploads to Supabase storage
   - Gets public URL: `https://xxx.supabase.co/storage/v1/object/public/bucket/funds-list.csv`
   - FUNDRAISE button becomes **enabled**

### **Phase 2: Data Processing**
3. **User clicks FUNDRAISE button**
   - Frontend calls backend `/fundraise` endpoint
   - Sends payload with both URLs
   - Backend processes everything automatically

### **Phase 3: Backend Processing**
4. **Backend workflow execution**
   - Downloads PDF from Supabase URL
   - Downloads CSV from Supabase URL
   - Parses PDF to extract business information
   - Processes CSV to extract fund data
   - Stores complete results in Supabase database

## 📱 **Frontend Implementation**

### **1. File Upload Components**

```typescript
// components/FileUpload.tsx
import { useState } from 'react';
import { supabase } from '../lib/supabase';

interface FileUploadProps {
  onUploadComplete: (url: string) => void;
  fileType: 'pdf' | 'csv';
  label: string;
}

export default function FileUpload({ onUploadComplete, fileType, label }: FileUploadProps) {
  const [uploading, setUploading] = useState(false);
  const [uploadedUrl, setUploadedUrl] = useState<string | null>(null);

  const handleUpload = async (file: File) => {
    try {
      setUploading(true);
      
      // Upload to Supabase storage
      const fileName = `${Date.now()}-${file.name}`;
      const { data, error } = await supabase.storage
        .from('uploads')
        .upload(fileName, file);

      if (error) throw error;

      // Get public URL
      const { data: { publicUrl } } = supabase.storage
        .from('uploads')
        .getPublicUrl(fileName);

      setUploadedUrl(publicUrl);
      onUploadComplete(publicUrl);
      
    } catch (error) {
      console.error('Upload error:', error);
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="file-upload">
      <label>{label}</label>
      <input
        type="file"
        accept={fileType === 'pdf' ? '.pdf' : '.csv'}
        onChange={(e) => e.target.files?.[0] && handleUpload(e.target.files[0])}
        disabled={uploading}
      />
      {uploading && <span>Uploading...</span>}
      {uploadedUrl && <span>✅ Uploaded: {uploadedUrl}</span>}
    </div>
  );
}
```

### **2. Main Fundraise Component**

```typescript
// components/FundraiseWorkflow.tsx
import { useState } from 'react';
import FileUpload from './FileUpload';

export default function FundraiseWorkflow() {
  const [pitchDeckUrl, setPitchDeckUrl] = useState<string | null>(null);
  const [fundsListUrl, setFundsListUrl] = useState<string | null>(null);
  const [processing, setProcessing] = useState(false);
  const [result, setResult] = useState<any>(null);

  const isFundraiseEnabled = pitchDeckUrl && fundsListUrl;

  const handleFundraise = async () => {
    if (!isFundraiseEnabled) return;

    try {
      setProcessing(true);
      
      // Call backend /fundraise endpoint
      const response = await fetch('/api/fundraise', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          pitchDeckLink: pitchDeckUrl,
          fundsListLink: fundsListUrl,
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      setResult(data);
      
    } catch (error) {
      console.error('Fundraise error:', error);
    } finally {
      setProcessing(false);
    }
  };

  return (
    <div className="fundraise-workflow">
      <h2>🚀 Fundraise Workflow</h2>
      
      {/* Phase 1: File Uploads */}
      <div className="upload-section">
        <h3>📄 Upload Files</h3>
        
        <FileUpload
          fileType="pdf"
          label="Pitch Deck PDF"
          onUploadComplete={setPitchDeckUrl}
        />
        
        <FileUpload
          fileType="csv"
          label="Funds List CSV"
          onUploadComplete={setFundsListUrl}
        />
      </div>

      {/* Phase 2: Fundraise Button */}
      <div className="fundraise-section">
        <button
          onClick={handleFundraise}
          disabled={!isFundraiseEnabled || processing}
          className={`fundraise-btn ${isFundraiseEnabled ? 'enabled' : 'disabled'}`}
        >
          {processing ? '🔄 Processing...' : '💰 FUNDRAISE'}
        </button>
        
        {!isFundraiseEnabled && (
          <p className="help-text">
            Upload both files to enable the FUNDRAISE button
          </p>
        )}
      </div>

      {/* Phase 3: Results */}
      {result && (
        <div className="results-section">
          <h3>✅ Results</h3>
          <div className="result-card">
            <h4>Company: {result.pitch_deck.company_name}</h4>
            <p>Description: {result.pitch_deck.description}</p>
            <p>Problem: {result.pitch_deck.problem}</p>
            <p>Solution: {result.pitch_deck.solution}</p>
            <p>Funding: {result.pitch_deck.funding_info}</p>
            <p>Industries: {result.pitch_deck.industry_sectors}</p>
            <p>Total Funds: {result.funds_list.total_funds}</p>
          </div>
        </div>
      )}
    </div>
  );
}
```

### **3. API Route Handler**

```typescript
// pages/api/fundraise.ts
import type { NextApiRequest, NextApiResponse } from 'next';

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  if (req.method !== 'POST') {
    return res.status(405).json({ message: 'Method not allowed' });
  }

  try {
    const { pitchDeckLink, fundsListLink } = req.body;

    if (!pitchDeckLink || !fundsListLink) {
      return res.status(400).json({ 
        message: 'Both pitchDeckLink and fundsListLink are required' 
      });
    }

    // Call your parser-agent backend
    const backendResponse = await fetch('http://localhost:8000/fundraise', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        pitch_deck_link: pitchDeckLink,
        funds_list_link: fundsListLink,
      }),
    });

    if (!backendResponse.ok) {
      const errorData = await backendResponse.text();
      throw new Error(`Backend error: ${errorData}`);
    }

    const data = await backendResponse.json();
    res.status(200).json(data);

  } catch (error) {
    console.error('API error:', error);
    res.status(500).json({ 
      message: 'Internal server error',
      error: error instanceof Error ? error.message : 'Unknown error'
    });
  }
}
```

## 🔧 **Backend Configuration**

### **1. Environment Variables**

Create a `.env.local` file in your Next.js project:

```env
# Supabase Configuration
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_anon_key

# Backend API
NEXT_PUBLIC_BACKEND_URL=http://localhost:8000

# Storage Bucket Names
NEXT_PUBLIC_STORAGE_BUCKET=uploads
```

### **2. Supabase Client Setup**

```typescript
// lib/supabase.ts
import { createClient } from '@supabase/supabase-js';

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!;
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!;

export const supabase = createClient(supabaseUrl, supabaseAnonKey);
```

## 📊 **Data Flow Details**

### **1. Pitch Deck Processing**

```
PDF Upload → Supabase Storage → Public URL → Backend Download → PyMuPDF Parse → Business Data
```

**Extracted Data:**
- Company Name
- Description
- Problem Statement
- Solution
- Funding Information
- Industry Sectors
- Page Count
- Text Length

### **2. Funds List Processing**

```
CSV Upload → Supabase Storage → Public URL → Backend Download → CSV Parse → Fund Data
```

**Extracted Data:**
- Total number of funds
- Individual fund information (as JSON)
- Raw CSV content (fallback)

### **3. Complete Workflow Storage**

```
Backend → Supabase Database → Structured Record → Frontend Display
```

**Stored Record:**
- Workflow ID (UUID)
- Both file URLs
- Extracted business data
- Processed fund data
- Processing timestamp
- Status information

## 🧪 **Testing the Integration**

### **1. Test Backend Endpoint**

```bash
# Test the /fundraise endpoint directly
curl -X POST "http://localhost:8000/fundraise" \
  -H "Content-Type: application/json" \
  -d '{
    "pitch_deck_link": "https://example.com/pitch-deck.pdf",
    "funds_list_link": "https://example.com/funds-list.csv"
  }'
```

### **2. Test Frontend Integration**

1. Start your Next.js app: `npm run dev`
2. Start the backend: `python api.py`
3. Upload sample files through the UI
4. Click FUNDRAISE button
5. Check results and database storage

## 🚨 **Error Handling**

### **Common Issues & Solutions**

1. **CORS Errors**
   - Backend already has CORS configured for n8n
   - Frontend should work without additional CORS setup

2. **File Download Failures**
   - Ensure Supabase URLs are public
   - Check file permissions in Supabase storage

3. **Parsing Errors**
   - Backend includes fallback CSV handling
   - PDF parsing errors are logged and returned

4. **Storage Failures**
   - Check Supabase connection
   - Verify table structure exists

## 🎯 **Production Considerations**

### **1. Security**
- Implement proper authentication
- Use environment variables for all secrets
- Consider Row Level Security (RLS) in Supabase

### **2. Performance**
- Add file size limits
- Implement progress indicators
- Consider async processing for large files

### **3. Monitoring**
- Add logging for debugging
- Monitor API response times
- Track success/failure rates

## 🎉 **Ready to Integrate!**

Your Next.js frontend can now:

✅ **Upload files** to Supabase storage  
✅ **Get public URLs** for backend processing  
✅ **Trigger fundraise workflow** with single button click  
✅ **Display results** from parsed data  
✅ **Store everything** in Supabase database  

The separation of concerns is maintained:
- **Frontend**: UI, file uploads, user interaction
- **Supabase**: File storage, database, public URLs
- **Backend**: File processing, parsing, data extraction

Start building your frontend components and test the integration! 🚀




