import os
import json
import logging
from datetime import datetime

def setup_logging():
    """Setup logging configuration"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('crawler.log'),
            logging.StreamHandler()
        ]
    )

def create_directories():
    """Create necessary directories"""
    directories = ['data/json', 'data/html']
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        logging.info(f"Created directory: {directory}")

def save_json(data, business_id):
    """Save data as JSON file"""
    filename = f"data/json/{business_id}.json"
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        logging.info(f"Saved JSON: {filename}")
        return True
    except Exception as e:
        logging.error(f"Error saving JSON {filename}: {e}")
        return False

def save_html(html_content, business_id):
    """Save HTML content"""
    filename = f"data/html/{business_id}.html"
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html_content)
        logging.info(f"Saved HTML: {filename}")
        return True
    except Exception as e:
        logging.error(f"Error saving HTML {filename}: {e}")
        return False

def clean_text(text):
    """Clean and normalize text"""
    if text:
        return ' '.join(text.strip().split())
    return ""