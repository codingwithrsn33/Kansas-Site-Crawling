# Enhanced Configuration settings
CONFIG = {
    'base_url': 'https://mibusinessregistry.lara.state.mi.us/search/business',
    'timeout': 30,
    'retry_attempts': 3,
    'delay_between_requests': 5,  # Increased for better politeness
    'max_searches_per_minute': 10,
    'output_format': 'json'
}

# Search terms (you can modify these)
SEARCH_TERMS = [
    "AAA Roofing LLP",
    "Test Company LLC",
    # Add more search terms here
]

# Error handling configuration
ERROR_CONFIG = {
    'save_html_on_errors': True,
    'log_level': 'INFO',
    'max_html_fallback_size_mb': 10
}