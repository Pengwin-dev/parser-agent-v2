#!/usr/bin/env python3
"""
Configuration file for the PDF Parser API
Contains Supabase and other configuration settings.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Supabase Configuration
SUPABASE_URL = os.getenv("SUPABASE_URL", "your_supabase_project_url")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "your_supabase_anon_key")

# Database table name
SUPABASE_TABLE = os.getenv("SUPABASE_TABLE", "pitch_decks")

# API Configuration
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8000"))

# File Storage
TEMP_DIR = os.getenv("TEMP_DIR", "temp_uploads")

