import requests
import time
from typing import Dict, List, Optional
from config import settings

class ArzinjaAPI:
    def __init__(self):
        self.base_url = settings.settings.ARZINJA_API_URL
        self.api_key = settings.settings.ARZINJA_API_KEY
        self.secret = settings.settings.ARZINJA_SECRET
        self.session = requests.Session()
        
        if self.api_key and self.secret:
            self.session.headers.update({
                'X-API-KEY': self.api_key,
                'X-API-SECRET': self.secret
            })
    
    def get_market_data(self, symbol: str, interval: str = "1h", limit: int = 500) -> Dict:
        """
        دریافت داده‌های بازار برای سیمبل مورد نظر
        """
        try:
            response = self.session.get(
                f"{self.base_url}/market/history",
                params={
                    "symbol": symbol,
                    "interval": interval,
                    "limit": limit
                }
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"API Error: {response.status_code}"}
                
        except Exception as e:
            return {"error": str(e)}
    
    def get_account_info(self) -> Dict:
        """
        دریافت اطلاعات حساب کاربری
        """
        try:
            response = self.session.get(f"{self.base_url}/account/info")
            
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"API Error: {response.status_code}"}
                
        except Exception as e:
            return {"error": str(e)}
    
    def execute_trade(self, symbol: str, trade_type: str, amount: float, 
                     price: Optional[float] = None) -> Dict:
        """
        اجرای معامله پیشرفته با کارمزد صفر
        """
        try:
            payload = {
                "symbol": symbol,
                "type": trade_type,
                "amount": amount,
                "fee_type": "zero"  # کارمزد صفر برای P2P
            }
            
            if price:
                payload["price"] = price
            
            response = self.session.post(
                f"{self.base_url}/trade/advanced",
                json=payload
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"API Error: {response.status_code}"}
                
        except Exception as e:
            return {"error": str(e)}
    
    def get_trading_pairs(self) -> List[str]:
        """
        دریافت لیست زوج‌های معاملاتی موجود
        """
        try:
            response = self.session.get(f"{self.base_url}/market/pairs")
            
            if response.status_code == 200:
                data = response.json()
                return [pair["symbol"] for pair in data]
            else:
                return []
                
        except Exception as e:
            print(f"Error fetching trading pairs: {e}")
            return []