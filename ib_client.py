"""
Interactive Brokers API Client Helper.

This module provides helper functions to interact with the Interactive Brokers API.
"""

import logging
import requests
import time
from datetime import datetime

logger = logging.getLogger(__name__)

class IBClient:
    """Client for interacting with Interactive Brokers API."""
    
    def __init__(self, base_url, verify_ssl=False):
        """
        Initialize the IB client.
        
        Args:
            base_url (str): Base URL for the IB API
            verify_ssl (bool): Whether to verify SSL certificates
        """
        self.base_url = base_url
        self.verify_ssl = verify_ssl
        self.session = None
        self.authenticated = False
        self.last_activity = None
    
    def create_session(self):
        """Create a new session."""
        self.session = requests.Session()
        self.authenticated = False
        return self.session
    
    def authenticate(self):
        """
        Authenticate with the IB API.
        
        Returns:
            bool: Whether authentication was successful
        """
        if not self.session:
            self.create_session()
        
        try:
            # Initial authentication
            auth_response = self.session.post(
                f"{self.base_url}/iserver/auth/ssodh/init",
                verify=self.verify_ssl
            )
            auth_response.raise_for_status()
            auth_data = auth_response.json()
            
            # Check if we need to validate
            if auth_data.get('challenge'):
                logger.info("Second factor authentication required")
                # In reality, this would need to handle the second factor
                # For demo purposes, we'll just sleep and check status
                time.sleep(2)
                
                # Check authentication status
                status_response = self.session.get(
                    f"{self.base_url}/iserver/auth/status",
                    verify=self.verify_ssl
                )
                status_data = status_response.json()
                
                if status_data.get('authenticated'):
                    self.authenticated = True
                    self.last_activity = datetime.now()
                    logger.info("Successfully authenticated with IB API")
                    return True
                else:
                    logger.error("Failed to authenticate with IB API")
                    return False
            
            # If no challenge, check if already authenticated
            if auth_data.get('authenticated'):
                self.authenticated = True
                self.last_activity = datetime.now()
                logger.info("Successfully authenticated with IB API")
                return True
            
            logger.error(f"Failed to authenticate with IB API: {auth_data}")
            return False
            
        except requests.RequestException as e:
            logger.error(f"Error authenticating with IB API: {str(e)}")
            return False
    
    def check_session(self):
        """
        Check if the current session is valid.
        
        Returns:
            bool: Whether the session is valid
        """
        if not self.session or not self.authenticated:
            return False
            
        try:
            status_response = self.session.get(
                f"{self.base_url}/iserver/auth/status",
                verify=self.verify_ssl
            )
            status_data = status_response.json()
            
            if status_data.get('authenticated'):
                self.last_activity = datetime.now()
                return True
            else:
                # Try to reauthenticate
                return self.authenticate()
                
        except requests.RequestException as e:
            logger.error(f"Error checking session: {str(e)}")
            return False
    
    def request(self, method, endpoint, **kwargs):
        """
        Make a request to the IB API.
        
        Args:
            method (str): HTTP method
            endpoint (str): API endpoint
            **kwargs: Additional arguments to pass to requests
            
        Returns:
            dict: Response data
        """
        if not self.check_session():
            if not self.authenticate():
                raise Exception("Failed to authenticate with IB API")
        
        url = f"{self.base_url}/{endpoint}"
        
        try:
            response = self.session.request(
                method, url, verify=self.verify_ssl, **kwargs
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Error making request to IB API: {str(e)}")
            raise
    
    def get_account_info(self):
        """
        Get account information.
        
        Returns:
            dict: Account information
        """
        return self.request('GET', 'portfolio/accounts')
    
    def get_portfolio(self, account_id):
        """
        Get portfolio for an account.
        
        Args:
            account_id (str): Account ID
            
        Returns:
            dict: Portfolio information
        """
        return self.request('GET', f'portfolio/{account_id}/positions')
    
    def get_market_data(self, conids):
        """
        Get market data for contract IDs.
        
        Args:
            conids (list): List of contract IDs
            
        Returns:
            dict: Market data
        """
        if isinstance(conids, (list, tuple)):
            conids = ','.join(map(str, conids))
            
        return self.request('GET', f'iserver/marketdata/snapshot?conids={conids}')

# Example usage
if __name__ == "__main__":
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    ib_api_url = os.getenv('IB_API_BASE_URL', 'https://localhost:5000/v1/portal')
    verify_ssl = os.getenv('VERIFY_SSL', 'False').lower() == 'true'
    
    client = IBClient(ib_api_url, verify_ssl)
    
    if client.authenticate():
        print("Authentication successful!")
        
        # Get account info
        accounts = client.get_account_info()
        print(f"Accounts: {accounts}")
        
        # If we have accounts, get portfolio for the first one
        if accounts and len(accounts) > 0:
            account_id = accounts[0].get('id')
            portfolio = client.get_portfolio(account_id)
            print(f"Portfolio: {portfolio}")
    else:
        print("Failed to authenticate with IB API")
