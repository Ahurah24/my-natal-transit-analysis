"""
کلاینت API برای ارزینجا
"""

import requests
import time
from typing import Dict, Any, Optional
import hashlib
import hmac
import json

class ArzinjaAPIClient:
    """
    کلاس کلاینت برای اتصال به API ارزینجا
    """
    
    def __init__(self, api_key: str, secret_key: str, base_url: str = "https://api-v2.arzinja.ir/api"):
        """
        مقداردهی اولیه کلاینت
        
        Args:
            api_key (str): کلید API
            secret_key (str): کلید مخفی API
            base_url (str): آدرس پایه API
        """
        self.api_key = api_key
        self.secret_key = secret_key
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'X-API-KEY': api_key
        })
        
    def _generate_signature(self, method: str, endpoint: str, params: Dict[str, Any]) -> str:
        """
        تولید امضای امنیتی برای درخواست‌ها
        
        Args:
            method (str): روش HTTP
            endpoint (str): اندپوینت API
            params (Dict[str, Any]): پارامترهای درخواست
            
        Returns:
            str: امضای تولید شده
        """
        # مرتب کردن پارامترها
        sorted_params = '&'.join([f"{k}={v}" for k, v in sorted(params.items())])
        
        # تولید امضای HMAC-SHA256
        message = f"{method}{endpoint}{sorted_params}"
        signature = hmac.new(
            self.secret_key.encode('utf-8'),
            message.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        return signature
        
    def _make_request(self, method: str, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        انجام درخواست API
        
        Args:
            method (str): روش HTTP
            endpoint (str): اندپوینت API
            params (Dict[str, Any]): پارامترهای درخواست
            
        Returns:
            Dict[str, Any]: پاسخ API
        """
        if params is None:
            params = {}
            
        url = f"{self.base_url}{endpoint}"
        
        # افزودن timestamp به پارامترها
        params['timestamp'] = int(time.time() * 1000)
        
        try:
            # تولید امضای درخواست
            signature = self._generate_signature(method, endpoint, params)
            params['signature'] = signature
            
            response = self.session.request(
                method=method,
                url=url,
                json=params if method in ['POST', 'PUT'] else None,
                params=params if method == 'GET' else None,
                timeout=30
            )
            
            return response.json()
            
        except Exception as e:
            raise Exception(f"خطا در اتصال به API: {str(e)}")
    
    def get_ticker(self, symbol: str) -> Dict[str, Any]:
        """
        دریافت تیکر ارز
        
        Args:
            symbol (str): نماد ارز
            
        Returns:
            Dict[str, Any]: اطلاعات تیکر
        """
        return self._make_request('GET', '/ticker', {'symbol': symbol})
    
    def get_orderbook(self, symbol: str, limit: int = 100) -> Dict[str, Any]:
        """
        دریافت کتاب سفارشات
        
        Args:
            symbol (str): نماد ارز
            limit (int): تعداد سفارشات
            
        Returns:
            Dict[str, Any]: اطلاعات کتاب سفارشات
        """
        return self._make_request('GET', '/orderbook', {'symbol': symbol, 'limit': limit})
    
    def get_klines(self, symbol: str, interval: str, limit: int = 100) -> Dict[str, Any]:
        """
        دریافت داده‌های کلاین (قیمت‌ها)
        
        Args:
            symbol (str): نماد ارز
            interval (str): بازه زمانی
            limit (int): تعداد داده‌ها
            
        Returns:
            Dict[str, Any]: اطلاعات کلاین
        """
        return self._make_request('GET', '/klines', {
            'symbol': symbol,
            'interval': interval,
            'limit': limit
        })
    
    def get_account_info(self) -> Dict[str, Any]:
        """
        دریافت اطلاعات حساب کاربری
        
        Returns:
            Dict[str, Any]: اطلاعات حساب
        """
        return self._make_request('GET', '/account')
    
    def place_order(self, symbol: str, side: str, type_: str, quantity: float, price: Optional[float] = None) -> Dict[str, Any]:
        """
        ثبت سفارش
        
        Args:
            symbol (str): نماد ارز
            side (str): جهت سفارش (BUY/SELL)
            type_ (str): نوع سفارش
            quantity (float): مقدار
            price (float): قیمت (در صورت لزوم)
            
        Returns:
            Dict[str, Any]: پاسخ ثبت سفارش
        """
        params = {
            'symbol': symbol,
            'side': side,
            'type': type_,
            'quantity': quantity
        }
        
        if price is not None:
            params['price'] = price
            
        return self._make_request('POST', '/order', params)
    
    def get_open_orders(self, symbol: str) -> Dict[str, Any]:
        """
        دریافت سفارشات باز
        
        Args:
            symbol (str): نماد ارز
            
        Returns:
            Dict[str, Any]: سفارشات باز
        """
        return self._make_request('GET', '/open-orders', {'symbol': symbol})
    
    def cancel_order(self, order_id: str) -> Dict[str, Any]:
        """
        لغو سفارش
        
        Args:
            order_id (str): شناسه سفارش
            
        Returns:
            Dict[str, Any]: پاسخ لغو سفارش
        """
        return self._make_request('DELETE', '/order', {'orderId': order_id})