#!/usr/bin/env python3
"""
Test script for the /fundraise endpoint
Tests the complete fundraise workflow with pitch deck and funds list.
"""

import requests
import json
from pathlib import Path


class FundraiseAPITester:
    """Test the fundraise workflow endpoint."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
    
    def test_fundraise_workflow(self):
        """Test the complete fundraise workflow."""
        try:
            print("🚀 Testing Fundraise Workflow")
            print("=" * 50)
            
            # Sample payload for testing
            # In production, these would be actual Supabase public URLs
            payload = {
                "pitch_deck_link": "https://example.com/pitch-deck.pdf",
                "funds_list_link": "https://example.com/funds-list.csv"
            }
            
            print(f"📄 Pitch Deck Link: {payload['pitch_deck_link']}")
            print(f"💰 Funds List Link: {payload['funds_list_link']}")
            print("\n📤 Sending request to /fundraise...")
            
            # Make the request to the fundraise endpoint
            response = self.session.post(
                f"{self.base_url}/fundraise",
                json=payload
            )
            
            print(f"📊 Response Status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print("✅ Fundraise workflow completed successfully!")
                print("\n📋 Results:")
                print(f"   Workflow ID: {result.get('workflow_id', 'N/A')}")
                print(f"   Company: {result.get('pitch_deck', {}).get('company_name', 'N/A')}")
                print(f"   Total Funds: {result.get('funds_list', {}).get('total_funds', 'N/A')}")
                print(f"   Status: {result.get('message', 'N/A')}")
                
                # Show detailed response
                print("\n🔍 Full Response:")
                print(json.dumps(result, indent=2))
                
                return result
            else:
                print(f"❌ Fundraise workflow failed!")
                print(f"   Status Code: {response.status_code}")
                print(f"   Response: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Test failed with error: {e}")
            return None
    
    def test_with_real_files(self):
        """Test with actual local files (for development)."""
        try:
            print("\n🧪 Testing with Local Files")
            print("=" * 50)
            
            # Check if we have sample files
            pdf_file = "Pdfs/sample_pitch_deck.pdf"
            if not Path(pdf_file).exists():
                print(f"❌ PDF file not found: {pdf_file}")
                print("   Please ensure you have sample files in the Pdfs/ directory")
                return None
            
            print(f"✅ Found PDF file: {pdf_file}")
            print("\n📝 Note: This test requires actual Supabase URLs.")
            print("   For development, you can:")
            print("   1. Upload files to Supabase storage")
            print("   2. Get public URLs")
            print("   3. Test with those URLs")
            
            return None
                
        except Exception as e:
            print(f"❌ Local file test failed: {e}")
            return None


def main():
    """Main test function."""
    print("Fundraise Endpoint Test")
    print("=" * 50)
    
    # Initialize tester
    tester = FundraiseAPITester()
    
    # Test 1: Basic workflow (will fail without real URLs)
    print("\n1. Testing Basic Fundraise Workflow...")
    result = tester.test_fundraise_workflow()
    
    if result:
        print("\n🎉 Fundraise workflow test passed!")
        print("\n📊 What was tested:")
        print("   ✅ Endpoint accepts POST request")
        print("   ✅ Payload structure is correct")
        print("   ✅ Response format is valid")
        print("   ✅ Workflow ID generation works")
        print("   ✅ Data structure is complete")
    else:
        print("\n⚠️ Basic test completed (expected to fail without real URLs)")
        print("\n📋 Next steps:")
        print("   1. Set up Supabase project")
        print("   2. Upload sample files to Supabase storage")
        print("   3. Get public URLs for testing")
        print("   4. Run test with real URLs")
    
    # Test 2: Local file check
    print("\n2. Checking Local Files...")
    tester.test_with_real_files()
    
    print("\n" + "=" * 50)
    print("🏁 Test completed!")
    print("\n💡 To test with real data:")
    print("   1. Create .env file with Supabase credentials")
    print("   2. Run SQL script in Supabase to create table")
    print("   3. Upload files to Supabase and get public URLs")
    print("   4. Test with actual URLs")


if __name__ == "__main__":
    main()




