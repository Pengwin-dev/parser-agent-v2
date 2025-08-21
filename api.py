#!/usr/bin/env python3
"""
FastAPI application for PDF Pitch Deck Parser
Provides REST endpoints for PDF processing and summary generation.
"""

from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import tempfile
import uuid
from pathlib import Path
from typing import Optional, Dict, Any
import json

from pdf_parser import PDFParser

# Import supabase service conditionally to avoid startup errors
try:
    from supabase_service import supabase_service
    SUPABASE_AVAILABLE = True
except Exception as e:
    print(f"⚠️ Supabase service not available: {e}")
    print("   The /fundraise endpoint will work but won't store data in Supabase")
    print("   Set up your .env file with Supabase credentials to enable full functionality")
    SUPABASE_AVAILABLE = False
    supabase_service = None


# Create FastAPI app
app = FastAPI(
    title="PDF Pitch Deck Parser API",
    description="API for extracting business information from PDF pitch decks",
    version="1.0.0"
)

# Add CORS middleware for n8n integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Store for temporary files (in production, use proper file storage)
TEMP_DIR = Path("temp_uploads")
TEMP_DIR.mkdir(exist_ok=True)


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "PDF Pitch Deck Parser API",
        "version": "1.0.0",
        "endpoints": {
            "POST /upload-pdf": "Upload and process a PDF file",
            "GET /health": "Health check endpoint",
            "GET /docs": "API documentation (Swagger UI)"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    return {"status": "healthy", "service": "PDF Parser API"}


@app.get("/health/supabase")
async def supabase_health_check():
    """Check Supabase connection health."""
    if not SUPABASE_AVAILABLE or not supabase_service:
        return {
            "status": "unhealthy",
            "service": "PDF Parser API + Supabase",
            "supabase_connected": False,
            "error": "Supabase service not available. Check your .env file configuration."
        }
    
    try:
        is_connected = supabase_service.test_connection()
        return {
            "status": "healthy" if is_connected else "unhealthy",
            "service": "PDF Parser API + Supabase",
            "supabase_connected": is_connected
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "service": "PDF Parser API + Supabase",
            "supabase_connected": False,
            "error": str(e)
        }


@app.post("/upload-pdf")
async def upload_and_process_pdf(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    return_summary: bool = True,
    save_file: bool = False
):
    """
    Upload a PDF file and extract business summary.
    
    Args:
        file: PDF file to upload
        return_summary: Whether to return the summary in response
        save_file: Whether to save the summary to a file
    
    Returns:
        JSON response with processing results
    """
    # Validate file type
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(
            status_code=400, 
            detail="Only PDF files are allowed"
        )
    
    # Generate unique filename
    file_id = str(uuid.uuid4())
    temp_pdf_path = TEMP_DIR / f"{file_id}_{file.filename}"
    temp_summary_path = TEMP_DIR / f"{file_id}_summary.txt"
    
    try:
        # Save uploaded file temporarily
        with open(temp_pdf_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Process PDF using our parser
        with PDFParser(str(temp_pdf_path)) as parser:
            if not parser.open_pdf():
                raise HTTPException(
                    status_code=500, 
                    detail="Failed to open PDF file"
                )
            
            # Extract text
            raw_text = parser.extract_all_text()
            if not raw_text:
                raise HTTPException(
                    status_code=500, 
                    detail="No text could be extracted from the PDF"
                )
            
            # Clean text
            cleaned_text = parser.clean_text(raw_text)
            
            # Generate summary
            summary = parser.generate_summary(cleaned_text)
            
            # Save summary if requested
            if save_file:
                output_file = parser.save_summary(summary, str(temp_summary_path))
                if not output_file:
                    raise HTTPException(
                        status_code=500, 
                        detail="Failed to save summary file"
                    )
            
            # Prepare response
            response_data = {
                "success": True,
                "file_id": file_id,
                "original_filename": file.filename,
                "pages_processed": len(parser.doc) if parser.doc else 0,
                "text_extracted_chars": len(cleaned_text),
                "summary_file_path": str(temp_summary_path) if save_file else None
            }
            
            # Include summary in response if requested
            if return_summary:
                # Parse the summary to extract structured data
                summary_data = parse_summary_to_dict(summary)
                response_data["summary"] = summary_data
            
            return JSONResponse(content=response_data, status_code=200)
    
    except Exception as e:
        # Clean up temporary files on error
        cleanup_temp_files(file_id)
        raise HTTPException(
            status_code=500, 
            detail=f"Error processing PDF: {str(e)}"
        )
    
    finally:
        # Clean up temporary PDF file
        if temp_pdf_path.exists():
            temp_pdf_path.unlink()


@app.get("/download-summary/{file_id}")
async def download_summary(file_id: str):
    """
    Download a generated summary file by file ID.
    
    Args:
        file_id: Unique identifier for the processed file
    
    Returns:
        Summary file as downloadable response
    """
    summary_path = TEMP_DIR / f"{file_id}_summary.txt"
    
    if not summary_path.exists():
        raise HTTPException(
            status_code=404, 
            detail="Summary file not found"
        )
    
    return FileResponse(
        path=str(summary_path),
        filename=f"summary_{file_id}.txt",
        media_type="text/plain"
    )


@app.get("/summary/{file_id}")
async def get_summary(file_id: str):
    """
    Get summary content by file ID without downloading.
    
    Args:
        file_id: Unique identifier for the processed file
    
    Returns:
        Summary content as JSON response
    """
    summary_path = TEMP_DIR / f"{file_id}_summary.txt"
    
    if not summary_path.exists():
        raise HTTPException(
            status_code=404, 
            detail="Summary file not found"
        )
    
    try:
        with open(summary_path, 'r', encoding='utf-8') as f:
            summary_content = f.read()
        
        # Parse summary to structured format
        summary_data = parse_summary_to_dict(summary_content)
        
        return {
            "success": True,
            "file_id": file_id,
            "summary": summary_data,
            "raw_summary": summary_content
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error reading summary file: {str(e)}"
        )


@app.delete("/cleanup/{file_id}")
async def cleanup_files(file_id: str):
    """
    Clean up temporary files for a specific file ID.
    
    Args:
        file_id: Unique identifier for the processed file
    
    Returns:
        Cleanup status
    """
    try:
        cleanup_temp_files(file_id)
        return {"success": True, "message": f"Cleaned up files for {file_id}"}
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error during cleanup: {str(e)}"
        )


from pydantic import BaseModel

class FundraiseRequest(BaseModel):
    pitch_deck_link: str
    funds_list_link: str

@app.post("/fundraise")
async def fundraise_workflow(request: FundraiseRequest):
    pitch_deck_link = request.pitch_deck_link
    funds_list_link = request.funds_list_link
    """
    Main fundraise workflow endpoint.
    
    This endpoint:
    1. Downloads the pitch deck from the provided link
    2. Downloads the funds list CSV from the provided link
    3. Parses the pitch deck to extract business information
    4. Processes the CSV to extract fund information
    5. Stores everything in Supabase
    
    Args:
        pitch_deck_link: Public URL to the pitch deck PDF
        funds_list_link: Public URL to the funds list CSV
    
    Returns:
        Complete workflow results with extracted data
    """
    try:
        import requests
        import tempfile
        import csv
        from io import StringIO
        
        print(f"🚀 Starting fundraise workflow...")
        print(f"📄 Pitch Deck: {pitch_deck_link}")
        print(f"💰 Funds List: {funds_list_link}")
        
        # Step 1: Download pitch deck PDF
        print("📥 Downloading pitch deck...")
        pitch_deck_response = requests.get(pitch_deck_link)
        if pitch_deck_response.status_code != 200:
            raise HTTPException(
                status_code=400,
                detail=f"Failed to download pitch deck: {pitch_deck_response.status_code}"
            )
        
        # Step 2: Download funds list CSV
        print("📥 Downloading funds list...")
        funds_list_response = requests.get(funds_list_link)
        if funds_list_response.status_code != 200:
            raise HTTPException(
                status_code=400,
                detail=f"Failed to download funds list: {funds_list_response.status_code}"
            )
        
        # Step 3: Process pitch deck
        print("🔍 Processing pitch deck...")
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_pdf:
            temp_pdf.write(pitch_deck_response.content)
            temp_pdf_path = temp_pdf.name
        
        try:
            with PDFParser(temp_pdf_path) as parser:
                if not parser.open_pdf():
                    raise HTTPException(
                        status_code=500,
                        detail="Failed to open downloaded PDF"
                    )
                
                # Extract and process text
                raw_text = parser.extract_all_text()
                if not raw_text:
                    raise HTTPException(
                        status_code=500,
                        detail="No text could be extracted from the PDF"
                    )
                
                cleaned_text = parser.clean_text(raw_text)
                summary = parser.generate_summary(cleaned_text)
                summary_data = parse_summary_to_dict(summary)
                
                print(f"✅ Pitch deck processed successfully")
                print(f"   Company: {summary_data.get('Company Name', 'N/A')}")
                print(f"   Pages: {summary_data.get('Total pages processed', 'N/A')}")
        
        finally:
            # Clean up temporary PDF file
            import os
            if os.path.exists(temp_pdf_path):
                os.unlink(temp_pdf_path)
        
        # Step 4: Process funds list CSV
        print("📊 Processing funds list...")
        csv_content = funds_list_response.text
        funds_data = []
        
        try:
            csv_reader = csv.DictReader(StringIO(csv_content))
            for row in csv_reader:
                funds_data.append(row)
            
            print(f"✅ Funds list processed successfully")
            print(f"   Total funds: {len(funds_data)}")
            
        except Exception as e:
            print(f"⚠️ Warning: CSV parsing failed, treating as text: {e}")
            # Fallback: treat as text if CSV parsing fails
            funds_data = [{"raw_content": csv_content}]
        
        # Step 5: Generate unique ID for this workflow
        workflow_id = str(uuid.uuid4())
        
        # Step 6: Store everything in Supabase (if available)
        stored_data = None
        if SUPABASE_AVAILABLE and supabase_service:
            print("💾 Storing data in Supabase...")
            try:
                stored_data = supabase_service.store_fundraise_data(
                    pitch_deck_link=pitch_deck_link,
                    funds_list_link=funds_list_link,
                    pitch_deck_data=summary_data,
                    funds_data=funds_data,
                    workflow_id=workflow_id
                )
                
                if stored_data:
                    print("✅ Data stored successfully in Supabase")
                else:
                    print("⚠️ Failed to store data in Supabase, but workflow completed")
            except Exception as e:
                print(f"⚠️ Supabase storage failed: {e}, but workflow completed")
        else:
            print("ℹ️ Supabase not available, skipping data storage")
        
        # Prepare response
        response_data = {
            "success": True,
            "message": "Fundraise workflow completed successfully",
            "workflow_id": workflow_id,
            "pitch_deck": {
                "company_name": summary_data.get("Company Name", "Not specified"),
                "description": summary_data.get("Description", "Not specified"),
                "problem": summary_data.get("Problem", "Not specified"),
                "solution": summary_data.get("Solution", "Not specified"),
                "funding_info": summary_data.get("Funding Info", "Not specified"),
                "industry_sectors": summary_data.get("Industry Sectors", "Not specified"),
                "pages_processed": summary_data.get("Total pages processed", 0),
                "text_extracted_chars": summary_data.get("Total text extracted", 0)
            },
            "funds_list": {
                "total_funds": len(funds_data),
                "sample_fund": funds_data[0] if funds_data else None
            },
            "links": {
                "pitch_deck": pitch_deck_link,
                "funds_list": funds_list_link
            },
            "supabase_stored": stored_data is not None,
            "stored_data": stored_data
        }
        
        return JSONResponse(content=response_data, status_code=200)
            
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        print(f"❌ Fundraise workflow failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Fundraise workflow failed: {str(e)}"
        )


@app.post("/store-pitch-deck")
async def store_pitch_deck_data(
    pitch_deck_link: str,
    funds_list_link: str,
    file_id: str
):
    """
    Store pitch deck data in Supabase with links.
    
    Args:
        pitch_deck_link: URL to the pitch deck
        funds_list_link: URL to the funds list
        file_id: File ID from previous PDF processing
    
    Returns:
        Stored data information
    """
    try:
        # Get the summary data for the file_id
        summary_path = TEMP_DIR / f"{file_id}_summary.txt"
        
        if not summary_path.exists():
            raise HTTPException(
                status_code=404, 
                detail="Summary file not found. Process PDF first."
            )
        
        # Read and parse the summary
        with open(summary_path, 'r', encoding='utf-8') as f:
            summary_content = f.read()
        
        summary_data = parse_summary_to_dict(summary_content)
        
        # Store in Supabase
        stored_data = supabase_service.store_pitch_deck_data(
            pitch_deck_link=pitch_deck_link,
            funds_list_link=funds_list_link,
            extracted_data=summary_data,
            original_filename=summary_data.get("original_filename", "unknown"),
            file_id=file_id
        )
        
        if stored_data:
            return {
                "success": True,
                "message": "Pitch deck data stored successfully",
                "file_id": file_id,
                "stored_data": stored_data
            }
        else:
            raise HTTPException(
                status_code=500, 
                detail="Failed to store data in Supabase"
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error storing pitch deck data: {str(e)}"
        )


@app.get("/pitch-decks/{file_id}")
async def get_pitch_deck_data(file_id: str):
    """
    Retrieve stored pitch deck data by file ID.
    
    Args:
        file_id: Unique identifier for the file
    
    Returns:
        Stored pitch deck data
    """
    try:
        data = supabase_service.get_pitch_deck_by_id(file_id)
        
        if data:
            return {
                "success": True,
                "data": data
            }
        else:
            raise HTTPException(
                status_code=404, 
                detail="Pitch deck data not found"
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error retrieving pitch deck data: {str(e)}"
        )


@app.get("/pitch-decks")
async def get_all_pitch_decks(limit: int = 100):
    """
    Retrieve all stored pitch deck records.
    
    Args:
        limit: Maximum number of records to return
    
    Returns:
        List of all pitch deck records
    """
    try:
        data = supabase_service.get_all_pitch_decks(limit=limit)
        
        return {
            "success": True,
            "count": len(data),
            "data": data
        }
            
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error retrieving pitch deck data: {str(e)}"
        )


def parse_summary_to_dict(summary_text: str) -> Dict[str, Any]:
    """
    Parse the summary text into a structured dictionary.
    
    Args:
        summary_text: Raw summary text from the parser
    
    Returns:
        Dictionary with structured summary data
    """
    lines = summary_text.split('\n')
    summary_data = {}
    
    current_key = None
    current_value = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Check if this is a key line (e.g., "Company Name:", "Problem:", etc.)
        if ':' in line and any(keyword in line for keyword in [
            'Company Name', 'Description', 'Problem', 'Solution', 
            'Funding Info', 'Industry Sectors', 'Total pages', 'Total text'
        ]):
            # Save previous key-value pair
            if current_key and current_value:
                summary_data[current_key] = '\n'.join(current_value).strip()
            
            # Start new key-value pair
            parts = line.split(':', 1)
            if len(parts) == 2:
                current_key = parts[0].strip()
                current_value = [parts[1].strip()] if parts[1].strip() else []
            else:
                current_key = line
                current_value = []
        else:
            # Continue building current value
            if current_key:
                current_value.append(line)
    
    # Save the last key-value pair
    if current_key and current_value:
        summary_data[current_key] = '\n'.join(current_value).strip()
    
    return summary_data


def cleanup_temp_files(file_id: str):
    """Clean up temporary files for a given file ID."""
    try:
        for file_path in TEMP_DIR.glob(f"{file_id}_*"):
            if file_path.exists():
                file_path.unlink()
    except Exception as e:
        print(f"Warning: Could not cleanup files for {file_id}: {e}")


# Background task to clean up old temporary files
@app.on_event("startup")
async def startup_event():
    """Clean up old temporary files on startup."""
    try:
        for file_path in TEMP_DIR.glob("*"):
            if file_path.exists():
                # Remove files older than 1 hour (for demo purposes)
                # In production, implement proper file lifecycle management
                file_path.unlink()
    except Exception as e:
        print(f"Warning: Could not cleanup old files: {e}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
