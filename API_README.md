# PDF Parser FastAPI

A FastAPI-based REST API that exposes the PDF Pitch Deck Parser functionality for easy integration with workflows and other applications.

## 🚀 Features

- **REST API**: Clean REST endpoints for PDF processing
- **File Upload**: Upload PDF files via HTTP POST
- **Structured Responses**: JSON responses with extracted business information
- **File Management**: Download summaries and manage temporary files
- **CORS Support**: Ready for web applications and n8n integration
- **Health Monitoring**: Built-in health check endpoints
- **Auto-documentation**: Swagger UI at `/docs`

## 📋 API Endpoints

### 1. **GET /** - Root Information
Returns API information and available endpoints.

**Response:**
```json
{
  "message": "PDF Pitch Deck Parser API",
  "version": "1.0.0",
  "endpoints": {
    "POST /upload-pdf": "Upload and process a PDF file",
    "GET /health": "Health check endpoint",
    "GET /docs": "API documentation (Swagger UI)"
  }
}
```

### 2. **GET /health** - Health Check
Returns API health status for monitoring.

**Response:**
```json
{
  "status": "healthy",
  "service": "PDF Parser API"
}
```

### 3. **POST /upload-pdf** - Process PDF
Upload and process a PDF file to extract business information.

**Parameters:**
- `file`: PDF file (multipart/form-data)
- `return_summary`: Boolean (default: true) - Include summary in response
- `save_file`: Boolean (default: false) - Save summary to file

**Response:**
```json
{
  "success": true,
  "file_id": "uuid-string",
  "original_filename": "presentation.pdf",
  "pages_processed": 5,
  "text_extracted_chars": 2500,
  "summary_file_path": "/path/to/summary.txt",
  "summary": {
    "Company Name": "TokenEstate",
    "Problem": "The traditional real estate market is illiquid...",
    "Solution": "TokenEstate is a decentralized platform...",
    "Funding Info": "$X Million Seed Round",
    "Industry Sectors": "Blockchain, Real Estate, Technology"
  }
}
```

### 4. **GET /summary/{file_id}** - Get Summary
Retrieve summary content by file ID.

**Response:**
```json
{
  "success": true,
  "file_id": "uuid-string",
  "summary": {
    "Company Name": "TokenEstate",
    "Problem": "The traditional real estate market is illiquid...",
    "Solution": "TokenEstate is a decentralized platform...",
    "Funding Info": "$X Million Seed Round",
    "Industry Sectors": "Blockchain, Real Estate, Technology"
  },
  "raw_summary": "Full summary text content..."
}
```

### 5. **GET /download-summary/{file_id}** - Download Summary
Download summary file as text file.

**Response:** File download

### 6. **DELETE /cleanup/{file_id}** - Cleanup Files
Remove temporary files for a specific file ID.

**Response:**
```json
{
  "success": true,
  "message": "Cleaned up files for uuid-string"
}
```

## 🛠️ Installation & Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Start the API Server
```bash
python api.py
```

The API will be available at `http://localhost:8000`

### 3. Access API Documentation
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 📱 Usage Examples

### Python Client Example
```python
import requests

# Upload PDF
files = {'file': open('presentation.pdf', 'rb')}
response = requests.post('http://localhost:8000/upload-pdf', files=files)

if response.status_code == 200:
    result = response.json()
    file_id = result['file_id']
    
    # Get summary
    summary_response = requests.get(f'http://localhost:8000/summary/{file_id}')
    summary = summary_response.json()
    
    print(f"Company: {summary['summary']['Company Name']}")
    print(f"Problem: {summary['summary']['Problem']}")
```

### cURL Examples
```bash
# Upload PDF
curl -X POST "http://localhost:8000/upload-pdf" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@presentation.pdf"

# Get summary
curl -X GET "http://localhost:8000/summary/{file_id}"

# Download summary file
curl -X GET "http://localhost:8000/download-summary/{file_id}" \
  -o summary.txt
```

## 🔗 n8n Integration

### HTTP Request Node Configuration

#### 1. **Upload PDF Node**
- **Method**: POST
- **URL**: `http://localhost:8000/upload-pdf`
- **Body**: Form-Data
  - Key: `file`
  - Value: File from previous node
- **Parameters**:
  - `return_summary`: true
  - `save_file`: true

#### 2. **Extract Summary Data Node**
- **Method**: GET
- **URL**: `http://localhost:8000/summary/{{$json.file_id}}`

#### 3. **Download Summary File Node**
- **Method**: GET
- **URL**: `http://localhost:8000/download-summary/{{$json.file_id}}`

### n8n Workflow Example

```
[File Trigger] → [HTTP Request: Upload PDF] → [HTTP Request: Get Summary] → [Process Data] → [Save to Database]
```

### Response Mapping in n8n

The API returns structured data that can be easily mapped in n8n:

```json
{
  "Company Name": "{{$json.summary.Company Name}}",
  "Problem": "{{$json.summary.Problem}}",
  "Solution": "{{$json.summary.Solution}}",
  "Funding": "{{$json.summary.Funding Info}}",
  "Industries": "{{$json.summary.Industry Sectors}}"
}
```

## 🧪 Testing

### Run Test Client
```bash
python test_api.py
```

This will test all endpoints with a sample PDF file.

### Manual Testing
1. Start the API server: `python api.py`
2. Open http://localhost:8000/docs
3. Use the interactive Swagger UI to test endpoints
4. Upload a PDF and see the extracted information

## 🔧 Configuration

### Environment Variables
- `HOST`: API host (default: 0.0.0.0)
- `PORT`: API port (default: 8000)
- `CORS_ORIGINS`: Comma-separated list of allowed origins

### Production Considerations
- **File Storage**: Replace temporary file storage with proper cloud storage
- **Authentication**: Add API key or JWT authentication
- **Rate Limiting**: Implement request rate limiting
- **Logging**: Add structured logging
- **Monitoring**: Add metrics and health checks
- **CORS**: Configure specific allowed origins

## 📊 Response Format

### Success Response
```json
{
  "success": true,
  "file_id": "uuid",
  "original_filename": "file.pdf",
  "pages_processed": 5,
  "text_extracted_chars": 2500,
  "summary": {
    "Company Name": "Company Name",
    "Problem": "Problem description",
    "Solution": "Solution description",
    "Funding Info": "Funding details",
    "Industry Sectors": "Industry list"
  }
}
```

### Error Response
```json
{
  "detail": "Error message description"
}
```

## 🚨 Error Handling

The API handles common errors:
- **400**: Invalid file type or missing file
- **404**: File or summary not found
- **500**: PDF processing errors or server issues

## 🔄 File Lifecycle

1. **Upload**: PDF is uploaded and processed
2. **Processing**: Text extraction and summary generation
3. **Storage**: Summary saved temporarily (if requested)
4. **Access**: Summary can be retrieved or downloaded
5. **Cleanup**: Temporary files removed automatically or manually

## 📈 Performance

- **Small PDFs** (< 1MB): ~1-2 seconds
- **Medium PDFs** (1-10MB): ~2-5 seconds
- **Large PDFs** (> 10MB): ~5-15 seconds

Processing time depends on:
- PDF size and complexity
- Number of pages
- Text density
- Server performance

## 🔐 Security Notes

- **File Validation**: Only PDF files are accepted
- **Temporary Storage**: Files are stored temporarily and cleaned up
- **CORS**: Configured for development (allow all origins)
- **No Authentication**: Add authentication for production use

## 🆘 Troubleshooting

### Common Issues

1. **Port Already in Use**
   ```bash
   # Change port in api.py or kill existing process
   netstat -ano | findstr :8000
   ```

2. **PDF Processing Fails**
   - Check PDF file integrity
   - Ensure PDF contains extractable text
   - Check server logs for errors

3. **File Not Found Errors**
   - Verify file ID is correct
   - Check if files were cleaned up
   - Ensure API server is running

### Debug Mode
Enable debug logging by setting log level in `api.py`:
```python
uvicorn.run("api:app", log_level="debug")
```

## 📞 Support

For issues or questions:
1. Check the API documentation at `/docs`
2. Review server logs for error details
3. Test with the provided test client
4. Verify PDF file format and content

---

**Ready for n8n Integration!** 🎯

The API is designed to work seamlessly with n8n workflows, providing structured data extraction from PDF pitch decks that can be easily processed and stored in your automation workflows.

