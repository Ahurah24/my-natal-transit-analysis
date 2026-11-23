"""
موتور تست‌های تاریخچه‌ای برای ربات معاملات ارزینجا
"""

import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
from api_client import ArzinjaAPIClient

class BacktestEngine:
    def __init__(self):
        self.client = ArzinjaAPIClient()
        
    def fetch_historical_data(self, symbol: str, days: int = 30) -> Dict:
        """
        دریافت داده‌های تاریخچه‌ای برای تست
        """
        try:
            # دریافت داده‌های کندلی 1 ساعته
            data = self.client.get_historical_data(symbol, interval="1h", limit=2000)
            
            if 'result' in data:
                return data['result']
            else:
                print(f"Error fetching historical data for {symbol}: {data}")
                return {}
                
        except Exception as e:
            print(f"Error fetching historical data: {e}")
            return {}

    def simple_moving_average(self, prices: List[float], window: int = 10) -> float:
        """
        محاسبه میانگین متحرک ساده
        """
        if len(prices) < window:
            return 0.0
            
        return sum(prices[-window:]) / window

    def run_basic_strategy_backtest(self, symbol: str, initial_balance: float = 1000000) -> Dict:
        """
        اجرای تست استراتژی پایه برای ربات معاملات
        """
        print(f"Running basic strategy backtest for {symbol}...")
        
        # دریافت داده‌ها
        data = self.fetch_historical_data(symbol, days=30)
        
        if not data:
            return {"error": "Failed to fetch historical data"}
        
        try:
            # استخراج قیمت‌ها
            prices = [float(item['close']) for item in data]
            
            # محاسبه اندیکاتورها
            ma_10 = self.simple_moving_average(prices, 10)
            ma_20 = self.simple_moving_average(prices, 20)
            
            # استراتژی ساده: خرید/فروش بر اساس میانگین‌ها
            position = None  # None, 'BUY', 'SELL'
            buy_price = 0.0
            total_profit = 0.0
            
            # محاسبه سود کل
            if len(prices) > 1:
                initial_price = prices[0]
                final_price = prices[-1]
                
                # نرخ بهره (در این تست ساده)
                profit_percentage = ((final_price - initial_price) / initial_price) * 100
                
                return {
                    "symbol": symbol,
                    "initial_balance": initial_balance,
                    "final_balance": initial_balance * (1 + profit_percentage/100),
                    "profit_percentage": profit_percentage,
                    "total_trades": len(prices) - 1,
                    "strategy": "Simple Moving Average",
                    "indicators": {
                        "ma_10": ma_10,
                        "ma_20": ma_20
                    },
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {"error": "Insufficient data for backtest"}
                
        except Exception as e:
            print(f"Error in backtest: {e}")
            return {"error": str(e)}