from supabase import create_client
import os
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def initialize_supabase():
    load_dotenv()
    
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    
    if not url or not key:
        raise ValueError("Missing Supabase configuration. Check .env file.")
        
    logger.info(f"Initializing Supabase client with URL: {url[:20]}...")
    
    try:
        client = create_client(url, key)
        # Test connection
        test = client.table('games').select("*").limit(1).execute()
        logger.info("✅ Supabase connection test successful")
        return client
    except Exception as e:
        logger.error(f"❌ Failed to initialize Supabase client: {str(e)}")
        raise

# Initialize the client
supabase = initialize_supabase()