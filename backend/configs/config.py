import os
import json
import logging

logger = logging.getLogger(__name__)

def set_envs():
    """Set up environment variables for the application"""
    try:
        # Google Cloud credentials are handled in main.py
        # Add any other environment variable setup here
        pass
    except Exception as e:
        logger.error(f"Error setting up environment variables: {e}")
        raise 