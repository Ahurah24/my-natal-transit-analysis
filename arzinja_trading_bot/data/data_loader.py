import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
import random
from datetime import datetime, timedelta

class DataLoader:
    def __init__(self):
        self.data = {}
    
    def generate_test_data(self, symbol: str, days: int = 30) -> Dict:
        """
        تولید داده‌های مصنوعی برای تست الگوریتم
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # ایجاد تاریخچه زمانی
        dates = pd.date_range(start=start_date, end=end_date, freq='1h')
        
        # تولید قیمت‌ها با الگوی realistic
        base_price = 50000  # مقدار پایه به تومان
        
        # ایجاد الگوی قیمت با نوسانات و روند
        prices = []
        current_price = base_price
        
        for i, date in enumerate(dates):
            # تغییرات روزانه (درصد)
            if i % 24 == 0:  # هر روز یک تغییر روند
                trend_change = random.uniform(-0.05, 0.05)  # تغییر روند نسبتاً کم
                base_price *= (1 + trend_change)
            
            # نوسانات کوتاه مدت
            change = random.uniform(-0.02, 0.02)  # نوسان ±2%
            current_price = max(1000, current_price * (1 + change))
            
            prices.append(current_price)
        
        # ایجاد داده‌های متنوع
        data = {
            'timestamp': dates,
            'open': prices[:-1],  # باز کردن
            'high': [max(prices[i], prices[i+1]) for i in range(len(prices)-1)],  # بالاترین قیمت
            'low': [min(prices[i], prices[i+1]) for i in range(len(prices)-1)],   # پایین‌ترین قیمت
            'close': prices[1:],  # بسته شدن
            'volume': [random.randint(100, 1000) for _ in range(len(prices)-1)]    # حجم معاملات
        }
        
        return {
            'symbol': symbol,
            'data': data,
            'timestamp': str(datetime.now())
        }
    
    def load_historical_data(self, api_client, symbol: str, days: int = 30) -> Dict:
        """
        بارگذاری داده‌های تاریخی از API
        """
        # در حالت تست، داده‌ها را از API دریافت می‌کنیم
        # در عمل این قسمت را با فراخوانی API پر می‌کنیم
        
        data = api_client.get_market_data(symbol, interval="1h", limit=days*24)
        
        if 'error' in data:
            print(f"Error loading historical data for {symbol}: {data['error']}")
            return None
            
        return data
    
    def prepare_features(self, raw_data: Dict) -> List[float]:
        """
        آماده‌سازی ویژگی‌ها برای استراتژی
        """
        if not raw_data or 'data' not in raw_data:
            return []
        
        prices = raw_data['data']['close']
        
        # اضافه کردن داده‌های مهم به عنوان ویژگی
        features = []
        
        # قیمت‌ها
        if len(prices) >= 50:
            features.extend(prices[-50:])  # آخرین 50 قیمت
            
        return features
    
    def get_market_data(self, symbol: str) -> Dict:
        """
        دریافت داده‌های بازار از API (برای تست)
        """
        data = self.generate_test_data(symbol, 30)
        
        # تبدیل timestamp به فرمت مناسب
        if 'timestamp' in data and isinstance(data['timestamp'], str):
            try:
                timestamp = datetime.fromisoformat(data['timestamp'].replace('Z', '+00:00'))
                data['timestamp'] = timestamp.strftime('%Y-%m-%d %H:%M:%S')
            except:
                pass
        
        return data