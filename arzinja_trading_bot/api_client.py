"""
کلاینت API ارزینجا برای اتصال به سرویس‌های معاملاتی
"""

import requests
import time
import hashlib
import hmac
import json
from urllib.parse import urlencode
from config import settings

class ArzinjaAPIClient:
    def __init__(self):
        self.base_url = settings.ARZINJA_API_URL
        self.api_key = settings.ARZINJA_API_KEY
        self.secret_key = settings.ARZINJA_SECRET
        self.session = requests.Session()
        
    def _generate_signature(self, params: dict) -> str:
        """تولید امضای امن برای درخواست‌ها"""
        if not self.secret_key:
            raise ValueError("SECRET_KEY is required")
            
        query_string = urlencode(params)
        return hmac.new(
            self.secret_key.encode('utf-8'),
            query_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
    
    def _make_request(self, method: str, endpoint: str, params: dict = None, data: dict = None) -> dict:
        """ارسال درخواست به API"""
        url = f"{self.base_url}{endpoint}"
        
        headers = {
            "X-API-KEY": self.api_key,
            "Content-Type": "application/json"
        }
        
        if params:
            # اضافه کردن امضای امن
            params['timestamp'] = int(time.time() * 1000)
            signature = self._generate_signature(params)
            params['signature'] = signature
            
        try:
            response = self.session.request(
                method=method,
                url=url,
                headers=headers,
                params=params,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                raise Exception(f"API Error: {response.status_code} - {response.text}")
                
        except requests.exceptions.RequestException as e:
            raise Exception(f"Request failed: {str(e)}")
    
    def get_tickers(self) -> dict:
        """دریافت قیمت‌های فعلی تمام ارزها"""
        return self._make_request("GET", "/ticker")
    
    def get_historical_data(self, symbol: str, interval: str = "1h", limit: int = 100) -> dict:
        """دریافت داده‌های تاریخچه‌ای"""
        params = {
            "symbol": symbol,
            "interval": interval,
            "limit": limit
        }
        return self._make_request("GET", "/klines", params=params)
    
    def get_account_info(self) -> dict:
        """دریافت اطلاعات حساب کاربری"""
        return self._make_request("GET", "/account")
    
    def place_order(self, symbol: str, side: str, quantity: float, price: float = None, 
                   order_type: str = "LIMIT") -> dict:
        """ثبت سفارش معاملاتی"""
        data = {
            "symbol": symbol,
            "side": side,  # BUY or SELL
            "quantity": quantity,
            "type": order_type
        }
        
        if price:
            data["price"] = price
            
        return self._make_request("POST", "/order", data=data)
    
    def get_order_status(self, symbol: str, order_id: str) -> dict:
        """دریافت وضعیت سفارش"""
        params = {
            "symbol": symbol,
            "orderId": order_id
        }
        return self._make_request("GET", "/order", params=params)
    
    def get_open_orders(self, symbol: str = None) -> dict:
        """دریافت سفارشات باز"""
        params = {}
        if symbol:
            params["symbol"] = symbol
            
        return self._make_request("GET", "/open-orders", params=params)

# تست اتصال به API
if __name__ == "__main__":
    client = ArzinjaAPIClient()
    try:
        print("Testing API connection...")
        tickers = client.get_tickers()
        print(f"Connected successfully. Got {len(tickers)} symbols")
    except Exception as e:
        print(f"Connection failed: {e}")