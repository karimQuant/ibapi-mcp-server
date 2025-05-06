"""
Configuration settings for the IB API Multi-Client Protocol Server.
"""

# Server Configuration
SERVER_HOST = '0.0.0.0'  # Listen on all interfaces
SERVER_PORT = 8080  # Default port for the server

# Interactive Brokers API Configuration
IB_API_HOST = 'localhost'  # IB Gateway host
IB_API_PORT = 5000  # Default IB Gateway port for Client Portal API
IB_API_BASE_URL = f'https://{IB_API_HOST}:{IB_API_PORT}/v1/portal'
VERIFY_SSL = False  # Whether to verify SSL certificates for IB API (often False for localhost)

# Authentication Configuration
JWT_SECRET = 'changeme_in_production'  # Secret key for JWT tokens
JWT_EXPIRY = 86400  # Token expiry in seconds (24 hours)

# Session Management
SESSION_TIMEOUT = 1800  # Session timeout in seconds (30 minutes)
SESSION_REFRESH = True  # Whether to refresh session on activity

# Logging Configuration
LOG_LEVEL = 'INFO'  # DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_FILE = 'server.log'
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

# Security Configuration
ALLOWED_ORIGINS = ['*']  # CORS origins, use specific domains in production
