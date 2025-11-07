"""
Bybit REST API client for authenticated trading operations.
"""
import time
import hmac
import hashlib
import requests
from typing import Dict, Optional, Any
from urllib.parse import urlencode
from ..utils.logger import get_logger

logger = get_logger(__name__)


class BybitRESTClient:
    """REST API client for Bybit authenticated operations."""
    
    def __init__(self, api_key: str, api_secret: str, base_url: str = "https://api.bybit.com"):
        """
        Initialize Bybit REST client.
        
        Args:
            api_key: Bybit API key
            api_secret: Bybit API secret
            base_url: Base URL for Bybit API
        """
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = base_url.rstrip("/")
        logger.info(f"Bybit REST client initialized for {self.base_url}")
    
    def _generate_signature(self, timestamp: str, recv_window: str, params: Dict[str, Any]) -> str:
        """
        Generate HMAC SHA256 signature for Bybit v5 API.
        
        Args:
            timestamp: Request timestamp in milliseconds
            recv_window: Receive window (e.g., "5000")
            params: Request parameters
            
        Returns:
            HMAC SHA256 signature
        """
        # Sort parameters by key
        sorted_params = sorted(params.items())
        param_str = "&".join([f"{k}={v}" for k, v in sorted_params])
        
        # Create signature payload
        payload = f"{timestamp}{self.api_key}{recv_window}{param_str}"
        
        # Generate signature
        signature = hmac.new(
            self.api_secret.encode("utf-8"),
            payload.encode("utf-8"),
            hashlib.sha256
        ).hexdigest()
        
        return signature
    
    def _send_request(self, method: str, endpoint: str, params: Optional[Dict] = None, signed: bool = False) -> Optional[Dict]:
        """
        Send authenticated request to Bybit API.
        
        Args:
            method: HTTP method ("GET" or "POST")
            endpoint: API endpoint (e.g., "/v5/order/create")
            params: Request parameters
            signed: Whether to sign the request
            
        Returns:
            JSON response or None if error
        """
        url = f"{self.base_url}{endpoint}"
        params = params or {}
        
        headers = {
            "Content-Type": "application/json"
        }
        
        if signed:
            # Generate timestamp and recv_window
            timestamp = str(int(time.time() * 1000))
            recv_window = "5000"
            
            # Add required parameters
            params["apiKey"] = self.api_key
            params["timestamp"] = timestamp
            params["recvWindow"] = recv_window
            
            # Generate signature
            signature = self._generate_signature(timestamp, recv_window, params)
            params["sign"] = signature
            
            # Add signature to headers
            headers["X-BAPI-API-KEY"] = self.api_key
            headers["X-BAPI-TIMESTAMP"] = timestamp
            headers["X-BAPI-RECV-WINDOW"] = recv_window
            headers["X-BAPI-SIGN"] = signature
        
        try:
            if method.upper() == "GET":
                response = requests.get(url, params=params, headers=headers, timeout=10)
            elif method.upper() == "POST":
                response = requests.post(url, json=params, headers=headers, timeout=10)
            else:
                logger.error(f"Unsupported HTTP method: {method}")
                return None
            
            response.raise_for_status()
            data = response.json()
            
            # Check Bybit response
            if data.get("retCode") != 0:
                logger.error(f"Bybit API error: {data.get('retMsg', 'Unknown error')} (code: {data.get('retCode')})")
                return None
            
            return data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Bybit REST request failed for {endpoint}: {e}")
            return None
        except Exception as e:
            logger.error(f"Error in Bybit REST request for {endpoint}: {e}", exc_info=True)
            return None
    
    def place_order(self, symbol: str, side: str, order_type: str, qty: str, 
                   price: Optional[str] = None, time_in_force: str = "GTC") -> Optional[Dict]:
        """
        Place a spot order on Bybit.
        
        Args:
            symbol: Trading symbol (e.g., "BTCUSDT")
            side: "Buy" or "Sell"
            order_type: "Market" or "Limit"
            qty: Order quantity (as string)
            price: Order price (required for Limit orders)
            time_in_force: "GTC", "IOC", "FOK" (default: "GTC")
            
        Returns:
            Order response or None if error
        """
        params = {
            "category": "spot",
            "symbol": symbol,
            "side": side,
            "orderType": order_type,
            "qty": qty,
            "timeInForce": time_in_force
        }
        
        if order_type == "Limit" and price:
            params["price"] = price
        
        logger.info(f"Placing Bybit order: {symbol} {side} {qty} @ {price or 'Market'}")
        response = self._send_request("POST", "/v5/order/create", params=params, signed=True)
        
        if response:
            result = response.get("result", {})
            order_id = result.get("orderId")
            logger.info(f"Bybit order placed successfully: {order_id}")
            return result
        
        return None
    
    def cancel_order(self, symbol: str, order_id: Optional[str] = None) -> Optional[Dict]:
        """
        Cancel an order on Bybit.
        
        Args:
            symbol: Trading symbol
            order_id: Order ID (if None, cancels all open orders for symbol)
            
        Returns:
            Cancel response or None if error
        """
        params = {
            "category": "spot",
            "symbol": symbol
        }
        
        if order_id:
            params["orderId"] = order_id
        
        logger.info(f"Cancelling Bybit order: {symbol} {order_id or 'all'}")
        response = self._send_request("POST", "/v5/order/cancel", params=params, signed=True)
        
        if response:
            logger.info(f"Bybit order cancelled successfully")
            return response.get("result", {})
        
        return None
    
    def get_open_orders(self, symbol: Optional[str] = None) -> Optional[Dict]:
        """
        Get open orders.
        
        Args:
            symbol: Trading symbol (optional, if None returns all)
            
        Returns:
            Open orders or None if error
        """
        params = {
            "category": "spot"
        }
        
        if symbol:
            params["symbol"] = symbol
        
        response = self._send_request("GET", "/v5/order/realtime", params=params, signed=True)
        
        if response:
            return response.get("result", {})
        
        return None
    
    def get_account_balance(self) -> Optional[Dict]:
        """
        Get account balance.
        
        Returns:
            Account balance or None if error
        """
        params = {
            "accountType": "SPOT"
        }
        
        response = self._send_request("GET", "/v5/account/wallet-balance", params=params, signed=True)
        
        if response:
            return response.get("result", {})
        
        return None


