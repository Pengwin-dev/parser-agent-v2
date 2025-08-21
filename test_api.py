#!/usr/bin/env python3
"""
Test client for the PDF Parser FastAPI
Demonstrates how to use the API endpoints.
"""

import requests
import json
from pathlib import Path


class PDFParserAPIClient:
    """Client for testing the PDF Parser API."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
    
    def health_check(self):
        """Test the health endpoint."""
        try:
            response = self.session.get(f"{self.base_url}/health")
            print(f"Health Check: {response.status_code}")
            print(f"Response: {response.json()}")
            return response.json()
        except Exception as e:
            print(f"Health check failed: {e}")
            return None
    
    def upload_pdf(self, pdf_path: str, return_summary: bool = True, save_file: bool = False):
        """
        Upload and process a PDF file.
        
        Args:
            pdf_path: Path to the PDF file
            return_summary: Whether to return summary in response
            save_file: Whether to save summary to file
        
        Returns:
            API response
        """
        try:
            # Check if file exists
            if not Path(pdf_path).exists():
                print(f"File not found: {pdf_path}")
                return None
            
            # Prepare files for upload
            files = {
                'file': ('test.pdf', open(pdf_path, 'rb'), 'application/pdf')
            }
            
            # Prepare parameters
            params = {
                'return_summary': return_summary,
                'save_file': save_file
            }
            
            print(f"Uploading PDF: {pdf_path}")
            response = self.session.post(
                f"{self.base_url}/upload-pdf",
                files=files,
                params=params
            )
            
            print(f"Upload Response: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"Success! File ID: {result.get('file_id')}")
                print(f"Pages processed: {result.get('pages_processed')}")
                
                if 'summary' in result:
                    print("\nExtracted Summary:")
                    for key, value in result['summary'].items():
                        print(f"{key}: {value}")
                
                return result
            else:
                print(f"Error: {response.status_code}")
                print(f"Response: {response.text}")
                return None
                
        except Exception as e:
            print(f"Upload failed: {e}")
            return None
    
    def get_summary(self, file_id: str):
        """Get summary by file ID."""
        try:
            response = self.session.get(f"{self.base_url}/summary/{file_id}")
            print(f"Get Summary Response: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"Summary for {file_id}:")
                for key, value in result['summary'].items():
                    print(f"{key}: {value}")
                return result
            else:
                print(f"Error: {response.status_code}")
                print(f"Response: {response.text}")
                return None
                
        except Exception as e:
            print(f"Get summary failed: {e}")
            return None
    
    def download_summary(self, file_id: str, output_path: str = None):
        """Download summary file by file ID."""
        try:
            response = self.session.get(f"{self.base_url}/download-summary/{file_id}")
            print(f"Download Response: {response.status_code}")
            
            if response.status_code == 200:
                if output_path is None:
                    output_path = f"downloaded_summary_{file_id}.txt"
                
                with open(output_path, 'wb') as f:
                    f.write(response.content)
                
                print(f"Summary downloaded to: {output_path}")
                return output_path
            else:
                print(f"Error: {response.status_code}")
                print(f"Response: {response.text}")
                return None
                
        except Exception as e:
            print(f"Download failed: {e}")
            return None
    
    def cleanup_files(self, file_id: str):
        """Clean up files for a specific file ID."""
        try:
            response = self.session.delete(f"{self.base_url}/cleanup/{file_id}")
            print(f"Cleanup Response: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"Cleanup result: {result}")
                return result
            else:
                print(f"Error: {response.status_code}")
                print(f"Response: {response.text}")
                return None
                
        except Exception as e:
            print(f"Cleanup failed: {e}")
            return None


def main():
    """Main test function."""
    print("PDF Parser API Test Client")
    print("=" * 40)
    
    # Initialize client
    client = PDFParserAPIClient()
    
    # Test health check
    print("\n1. Testing Health Check...")
    client.health_check()
    
    # Test PDF upload (use one of your sample PDFs)
    pdf_file = "Pdfs/sample_pitch_deck.pdf"
    
    if Path(pdf_file).exists():
        print(f"\n2. Testing PDF Upload with {pdf_file}...")
        result = client.upload_pdf(pdf_file, return_summary=True, save_file=True)
        
        if result and 'file_id' in result:
            file_id = result['file_id']
            
            print(f"\n3. Testing Get Summary for {file_id}...")
            client.get_summary(file_id)
            
            print(f"\n4. Testing Download Summary for {file_id}...")
            client.download_summary(file_id)
            
            print(f"\n5. Testing Cleanup for {file_id}...")
            client.cleanup_files(file_id)
        else:
            print("Upload failed, skipping other tests")
    else:
        print(f"PDF file not found: {pdf_file}")
        print("Please ensure you have a PDF file to test with")


if __name__ == "__main__":
    main()

