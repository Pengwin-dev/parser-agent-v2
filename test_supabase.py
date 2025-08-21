#!/usr/bin/env python3
"""
Test script for Supabase integration
Tests the new endpoints for storing pitch deck data.
"""

import requests
import json
from pathlib import Path


class SupabaseAPITester:
    """Test the Supabase integration endpoints."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
    
    def test_supabase_health(self):
        """Test the Supabase health endpoint."""
        try:
            response = self.session.get(f"{self.base_url}/health/supabase")
            print(f"Supabase Health Check: {response.status_code}")
            print(f"Response: {response.json()}")
            return response.json()
        except Exception as e:
            print(f"Supabase health check failed: {e}")
            return None
    
    def test_upload_and_store_workflow(self):
        """Test the complete workflow: upload PDF, then store with links."""
        try:
            # Step 1: Upload PDF
            pdf_file = "Pdfs/sample_pitch_deck.pdf"
            if not Path(pdf_file).exists():
                print(f"PDF file not found: {pdf_file}")
                return None
            
            print(f"\n1. Uploading PDF: {pdf_file}")
            files = {'file': ('test.pdf', open(pdf_file, 'rb'), 'application/pdf')}
            params = {'return_summary': True, 'save_file': True}
            
            upload_response = self.session.post(
                f"{self.base_url}/upload-pdf",
                files=files,
                params=params
            )
            
            if upload_response.status_code != 200:
                print(f"Upload failed: {upload_response.status_code}")
                return None
            
            upload_result = upload_response.json()
            file_id = upload_result['file_id']
            print(f"✅ Upload successful! File ID: {file_id}")
            
            # Step 2: Store data with links
            print(f"\n2. Storing pitch deck data with links...")
            
            # Sample links (replace with your actual links)
            payload = {
                "pitch_deck_link": "https://example.com/pitch-deck.pdf",
                "funds_list_link": "https://example.com/funds-list.pdf",
                "file_id": file_id
            }
            
            store_response = self.session.post(
                f"{self.base_url}/store-pitch-deck",
                json=payload
            )
            
            if store_response.status_code == 200:
                store_result = store_response.json()
                print(f"✅ Data stored successfully!")
                print(f"Stored data: {json.dumps(store_result, indent=2)}")
                
                # Step 3: Retrieve stored data
                print(f"\n3. Retrieving stored data...")
                retrieve_response = self.session.get(f"{self.base_url}/pitch-decks/{file_id}")
                
                if retrieve_response.status_code == 200:
                    retrieve_result = retrieve_response.json()
                    print(f"✅ Data retrieved successfully!")
                    print(f"Retrieved data: {json.dumps(retrieve_result, indent=2)}")
                else:
                    print(f"❌ Failed to retrieve data: {retrieve_response.status_code}")
                
                return store_result
            else:
                print(f"❌ Failed to store data: {store_response.status_code}")
                print(f"Response: {store_response.text}")
                return None
                
        except Exception as e:
            print(f"Workflow test failed: {e}")
            return None
    
    def test_get_all_pitch_decks(self):
        """Test retrieving all pitch deck records."""
        try:
            print(f"\n4. Testing get all pitch decks...")
            response = self.session.get(f"{self.base_url}/pitch-decks?limit=10")
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Retrieved {result['count']} pitch deck records")
                return result
            else:
                print(f"❌ Failed to retrieve all pitch decks: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"Get all pitch decks failed: {e}")
            return None


def main():
    """Main test function."""
    print("Supabase Integration Test")
    print("=" * 50)
    
    # Initialize tester
    tester = SupabaseAPITester()
    
    # Test Supabase health
    print("\n1. Testing Supabase Health...")
    health_result = tester.test_supabase_health()
    
    if health_result and health_result.get('supabase_connected'):
        print("✅ Supabase is connected!")
        
        # Test complete workflow
        print("\n2. Testing Complete Workflow...")
        workflow_result = tester.test_upload_and_store_workflow()
        
        if workflow_result:
            # Test retrieving all records
            tester.test_get_all_pitch_decks()
            
            print("\n🎉 All tests passed! Supabase integration is working.")
        else:
            print("\n❌ Workflow test failed.")
    else:
        print("\n❌ Supabase is not connected. Check your configuration.")
        print("Make sure to:")
        print("1. Set SUPABASE_URL and SUPABASE_KEY in your .env file")
        print("2. Run the SQL script in Supabase to create the table")
        print("3. Check your Supabase project settings")


if __name__ == "__main__":
    main()

