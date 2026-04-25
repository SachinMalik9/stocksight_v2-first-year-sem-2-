import time
import logging
import os
from elasticsearch import Elasticsearch
from src.config import config

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

def get_es_client():
    """
    Initializes the Elasticsearch client with a retry loop.
    """
    # Use getattr to prevent the 'AttributeError' if the config name is different
    es_url = getattr(config, 'ELASTICSEARCH_URL', "http://elasticsearch:9200")
    
    es = Elasticsearch(es_url)
    
    # Attempt to connect up to 10 times
    for i in range(10):
        try:
            if es.ping():
                logger.info("✅ Successfully connected to Elasticsearch.")
                return es
        except Exception:
            pass
        
        logger.warning(f"⏳ Waiting for Elasticsearch at {es_url}... (Attempt {i+1}/10)")
        time.sleep(5)
    
    logger.error("❌ Could not connect to Elasticsearch.")
    return None

# Global client instance
es_client = get_es_client()