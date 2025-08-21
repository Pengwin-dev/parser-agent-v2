#!/usr/bin/env python3
"""
Supabase service for PDF Parser API
Handles database operations for storing pitch deck data.
"""

from supabase import create_client, Client
from typing import Dict, Any, Optional
import json
from datetime import datetime
from config import SUPABASE_URL, SUPABASE_KEY, SUPABASE_TABLE


class SupabaseService:
    """Service class for Supabase operations."""
    
    def __init__(self):
        """Initialize Supabase client."""
        self.supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        self.table = SUPABASE_TABLE
    
    def test_connection(self) -> bool:
        """
        Test the Supabase connection.
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            # Try to fetch a single row to test connection
            response = self.supabase.table(self.table).select("*").limit(1).execute()
            return True
        except Exception as e:
            print(f"Supabase connection test failed: {e}")
            return False
    
    def store_pitch_deck_data(
        self, 
        pitch_deck_link: str, 
        funds_list_link: str,
        extracted_data: Dict[str, Any],
        original_filename: str,
        file_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Store pitch deck data in Supabase.
        
        Args:
            pitch_deck_link: URL to the pitch deck
            funds_list_link: URL to the funds list
            extracted_data: Structured data extracted from PDF
            original_filename: Original PDF filename
            file_id: Unique identifier for the file
            
        Returns:
            Dict with stored data or None if failed
        """
        try:
            # Prepare data for storage
            data_to_store = {
                "id": file_id,
                "pitch_deck_link": pitch_deck_link,
                "funds_list_link": funds_list_link,
                "original_filename": original_filename,
                "company_name": extracted_data.get("Company Name", "Not specified"),
                "description": extracted_data.get("Description", "Not specified"),
                "problem": extracted_data.get("Problem", "Not specified"),
                "solution": extracted_data.get("Solution", "Not specified"),
                "funding_info": extracted_data.get("Funding Info", "Not specified"),
                "industry_sectors": extracted_data.get("Industry Sectors", "Not specified"),
                "pages_processed": extracted_data.get("Total pages processed", 0),
                "text_extracted_chars": extracted_data.get("Total text extracted", 0),
                "extracted_at": datetime.utcnow().isoformat(),
                "raw_summary": json.dumps(extracted_data, ensure_ascii=False)
            }
            
            # Insert data into Supabase
            response = self.supabase.table(self.table).insert(data_to_store).execute()
            
            if response.data:
                print(f"Successfully stored pitch deck data for {file_id}")
                return response.data[0]
            else:
                print(f"Failed to store pitch deck data for {file_id}")
                return None
                
        except Exception as e:
            print(f"Error storing pitch deck data: {e}")
            return None
    
    def get_pitch_deck_by_id(self, file_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve pitch deck data by file ID.
        
        Args:
            file_id: Unique identifier for the file
            
        Returns:
            Dict with stored data or None if not found
        """
        try:
            response = self.supabase.table(self.table).select("*").eq("id", file_id).execute()
            
            if response.data:
                return response.data[0]
            return None
            
        except Exception as e:
            print(f"Error retrieving pitch deck data: {e}")
            return None
    
    def get_all_pitch_decks(self, limit: int = 100) -> list:
        """
        Retrieve all pitch deck records.
        
        Args:
            limit: Maximum number of records to return
            
        Returns:
            List of pitch deck records
        """
        try:
            response = self.supabase.table(self.table).select("*").limit(limit).execute()
            return response.data or []
            
        except Exception as e:
            print(f"Error retrieving all pitch decks: {e}")
            return []
    
    def update_pitch_deck(
        self, 
        file_id: str, 
        update_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Update pitch deck data.
        
        Args:
            file_id: Unique identifier for the file
            update_data: Data to update
            
        Returns:
            Updated data or None if failed
        """
        try:
            response = self.supabase.table(self.table).update(update_data).eq("id", file_id).execute()
            
            if response.data:
                return response.data[0]
            return None
            
        except Exception as e:
            print(f"Error updating pitch deck data: {e}")
            return None
    
    def delete_pitch_deck(self, file_id: str) -> bool:
        """
        Delete pitch deck record.
        
        Args:
            file_id: Unique identifier for the file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            response = self.supabase.table(self.table).delete().eq("id", file_id).execute()
            return True
            
        except Exception as e:
            print(f"Error deleting pitch deck data: {e}")
            return False
    
    def store_fundraise_data(
        self,
        pitch_deck_link: str,
        funds_list_link: str,
        pitch_deck_data: Dict[str, Any],
        funds_data: list,
        workflow_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Store complete fundraise workflow data in Supabase.
        
        Args:
            pitch_deck_link: URL to the pitch deck
            funds_list_link: URL to the funds list
            pitch_deck_data: Extracted business information
            funds_data: List of fund information
            workflow_id: Unique identifier for the workflow
            
        Returns:
            Dict with stored data or None if failed
        """
        try:
            # Prepare data for storage
            data_to_store = {
                "id": workflow_id,
                "pitch_deck_link": pitch_deck_link,
                "funds_list_link": funds_list_link,
                "workflow_type": "fundraise",
                "company_name": pitch_deck_data.get("Company Name", "Not specified"),
                "description": pitch_deck_data.get("Description", "Not specified"),
                "problem": pitch_deck_data.get("Problem", "Not specified"),
                "solution": pitch_deck_data.get("Solution", "Not specified"),
                "funding_info": pitch_deck_data.get("Funding Info", "Not specified"),
                "industry_sectors": pitch_deck_data.get("Industry Sectors", "Not specified"),
                "pages_processed": pitch_deck_data.get("Total pages processed", 0),
                "text_extracted_chars": pitch_deck_data.get("Total text extracted", 0),
                "total_funds": len(funds_data),
                "funds_data": json.dumps(funds_data, ensure_ascii=False),
                "extracted_at": datetime.utcnow().isoformat(),
                "raw_summary": json.dumps(pitch_deck_data, ensure_ascii=False),
                "status": "completed"
            }
            
            # Insert data into Supabase
            response = self.supabase.table(self.table).insert(data_to_store).execute()
            
            if response.data:
                print(f"Successfully stored fundraise data for workflow {workflow_id}")
                return response.data[0]
            else:
                print(f"Failed to store fundraise data for workflow {workflow_id}")
                return None
                
        except Exception as e:
            print(f"Error storing fundraise data: {e}")
            return None


# Create a global instance
supabase_service = SupabaseService()
