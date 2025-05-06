#!/usr/bin/env python3
"""
Interactive Brokers API Multi-Client Protocol Server

This server acts as a middleware between multiple clients and the 
Interactive Brokers Client Portal API, allowing multiple simultaneous connections.
"""

import os
import json
import logging
import requests
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import jwt
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("server.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Constants
DEFAULT_PORT = int(os.getenv('SERVER_PORT', 8080))
IB_API_BASE_URL = os.getenv('IB_API_BASE_URL', 'https://localhost:5000/v1/portal')
JWT_SECRET = os.getenv('JWT_SECRET', 'changeme_in_production')
JWT_EXPIRY = int(os.getenv('JWT_EXPIRY', 86400))  # Default 24 hours
VERIFY_SSL = os.getenv('VERIFY_SSL', 'False').lower() == 'true'

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# In-memory session store (consider using Redis in production)
active_sessions = {}

def get_ib_session(force_new=False):
    """
    Get or create an IB API session
    
    Args:
        force_new (bool): Force creation of a new session
        
    Returns:
        requests.Session: Active session
    """
    session_key = 'ib_session'
    
    # Check if we need a new session
    if force_new or session_key not in active_sessions:
        logger.info("Creating new IB API session")
        
        # Create new session
        session = requests.Session()
        
        # Authenticate with IB
        try:
            auth_response = session.post(
                f"{IB_API_BASE_URL}/iserver/auth/ssodh/init", 
                verify=VERIFY_SSL
            )
            auth_response.raise_for_status()
            auth_data = auth_response.json()
            
            # Check auth status
            if 'authenticated' in auth_data and auth_data['authenticated']:
                logger.info("Successfully authenticated with IB API")
                active_sessions[session_key] = {
                    'session': session,
                    'created_at': datetime.now(),
                    'last_used': datetime.now()
                }
            else:
                logger.error(f"Failed to authenticate with IB API: {auth_data}")
                return None
                
        except requests.RequestException as e:
            logger.error(f"Error connecting to IB API: {str(e)}")
            return None
    else:
        # Update last used timestamp
        active_sessions[session_key]['last_used'] = datetime.now()
    
    return active_sessions[session_key]['session']

def is_authenticated(req):
    """Check if the request is authenticated"""
    auth_header = req.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return False
    
    token = auth_header.split(' ')[1]
    try:
        jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        return True
    except jwt.PyJWTError:
        return False

@app.route('/api/auth', methods=['POST'])
def authenticate():
    """Authenticate a client"""
    # For simplicity, we're using a very basic auth mechanism
    # In production, implement proper authentication
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    # In a real app, validate credentials against a database
    # For now, we just check if we can auth with IB
    ib_session = get_ib_session(force_new=True)
    
    if ib_session:
        # Generate JWT token
        payload = {
            'sub': username,
            'iat': datetime.utcnow(),
            'exp': datetime.utcnow() + timedelta(seconds=JWT_EXPIRY)
        }
        token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")
        
        return jsonify({
            'token': token,
            'expires_in': JWT_EXPIRY
        })
    
    return jsonify({
        'error': 'Authentication failed'
    }), 401

@app.route('/api/status', methods=['GET'])
def status():
    """Get server status"""
    if not is_authenticated(request):
        return jsonify({'error': 'Unauthorized'}), 401
        
    ib_session = get_ib_session()
    if not ib_session:
        return jsonify({
            'status': 'error',
            'message': 'Not connected to IB API'
        }), 500
    
    # Check IB connection status
    try:
        status_response = ib_session.get(
            f"{IB_API_BASE_URL}/iserver/auth/status",
            verify=VERIFY_SSL
        )
        status_data = status_response.json()
        
        return jsonify({
            'status': 'ok',
            'connected': True,
            'ib_status': status_data,
            'server_time': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Error checking IB status: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/ib/<path:endpoint>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def proxy_to_ib(endpoint):
    """Proxy requests to the IB API"""
    if not is_authenticated(request):
        return jsonify({'error': 'Unauthorized'}), 401
        
    ib_session = get_ib_session()
    if not ib_session:
        return jsonify({
            'error': 'Failed to connect to IB API'
        }), 500
    
    # Build target URL
    target_url = f"{IB_API_BASE_URL}/{endpoint}"
    
    try:
        # Forward the request to IB API
        if request.method == 'GET':
            response = ib_session.get(
                target_url,
                params=request.args,
                verify=VERIFY_SSL
            )
        elif request.method == 'POST':
            response = ib_session.post(
                target_url,
                json=request.json,
                verify=VERIFY_SSL
            )
        elif request.method == 'PUT':
            response = ib_session.put(
                target_url,
                json=request.json,
                verify=VERIFY_SSL
            )
        elif request.method == 'DELETE':
            response = ib_session.delete(
                target_url,
                verify=VERIFY_SSL
            )
        
        # Return the response from IB
        return Response(
            response.content,
            status=response.status_code,
            content_type=response.headers.get('Content-Type', 'application/json')
        )
        
    except requests.RequestException as e:
        logger.error(f"Error proxying request to IB API: {str(e)}")
        return jsonify({
            'error': str(e)
        }), 500

if __name__ == '__main__':
    logger.info(f"Starting IB API Multi-Client Protocol Server on port {DEFAULT_PORT}")
    app.run(host='0.0.0.0', port=DEFAULT_PORT, debug=True)
