"""
database.py - Supabase PostgreSQL connection helper
"""

import os
from typing import Optional
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables from backend/ or project root .env
load_dotenv()
parent_env = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
if os.path.exists(parent_env):
    load_dotenv(parent_env)

# Lazy-initialised singleton — created on first use, not at import time
_supabase_client: Optional[Client] = None


def get_supabase() -> Client:
    """Return the shared Supabase client, creating it on first call.

    Raises:
        ValueError: If SUPABASE_URL or SUPABASE_KEY are not set in the environment.
    """
    global _supabase_client

    if _supabase_client is None:
        url = os.getenv("SUPABASE_URL", "")
        key = os.getenv("SUPABASE_KEY", "")
        if not url:
            raise ValueError(
                "Missing environment variable: SUPABASE_URL. "
                "Add it to your .env file or host environment settings."
            )
        if not key:
            raise ValueError(
                "Missing environment variable: SUPABASE_KEY. "
                "Add it to your .env file or host environment settings."
            )
        _supabase_client = create_client(url, key)

    return _supabase_client
