"""
بک تست ربات معاملات ارزینجا با استراتژی پیشرفته P2P
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List
import random

# اضافه کردن مسیر به پکیج‌ها
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

class Backtester:
    def __init__(self):
        self.name = "Arzinja_Advanced_Backtester"
        
    def generate_sample_data(self, symbol: str, days: int = 30) -> List[float]:
        """
        تولید داده نمونه برای بک تست
        """
        # قیمت شروع با توجه به نوع ارز
        base_prices = {
            "BTC": 50000,
            "ETH": 3000,
            "USDT": 1,
            "BNB": 400
        }
        
        start_price = base_prices.get(symbol, 1000)
        prices = [start_price]
        
        # تولید داده با روند و نوسانات realistic
        for i in range(1, days * 24):  # هر ساعت یک داده
            # نوسانات تصادفی با روند کلی
            change_percent = random.uniform(-0.05, 0.05)  # -5% تا +5%
            
            # اضافه کردن روند کلی (مثلاً صعودی 1% در روز)
            trend_change = 0.0004 * 24  # 1% در هفته
            change_percent += trend_change
            
            new_price = prices[-1] * (1 + change_percent)
            
            # اطمینان از اینکه قیمت منفی نباشد
            if new_price < 0.01:
                new_price = 0.01
                
            prices.append(new_price)
        
        return prices
    
    def run_backtest(self, strategy_name: str, symbol: str, 
                    price_data: List[float], initial_balance: float = 1000000) -> Dict:
        """
        اجرای بک تست با استراتژی پیشرفته
        """
        # اینجا می‌توانید استراتژی مورد نظر را فراخوانی کنید
        from strategies.p2p_advanced_strategy import P2PAdvancedStrategy
        
        strategy = P2PAdvancedStrategy()
        
        # اجرای معاملات پیشرفته
        result = strategy.execute_advanced_trade(
            symbol=symbol,
            price_data=price_data,
            initial_balance=initial_balance
        )
        
        return result
    
    def compare_strategies(self, symbols: List[str], days: int = 30) -> Dict:
        """
        مقایسه استراتژی‌های مختلف با داده نمونه
        """
        results = {}
        
        for symbol in symbols:
            # تولید داده نمونه
            price_data = self.generate_sample_data(symbol, days)
            
            print(f"Running backtest for {symbol}...")
            
            # بک تست استراتژی پیشرفته
            result = self.run_backtest("P2P_Advanced", symbol, price_data)
            
            results[symbol] = {
                "strategy": result.get("strategy"),
                "initial_balance": result.get("initial_balance"),
                "final_balance": result.get("final_balance"),
                "total_trades": result.get("total_trades"),
                "profit_percentage": result.get("profit_percentage"),
                "total_profit": result.get("total_profit"),
                "advanced_trading_type": result.get("advanced_trading_type"),
                "zero_fee_support": result.get("zero_fee_support"),
                "timestamp": datetime.now().isoformat()
            }
            
        return results
    
    def save_results(self, results: Dict, filename: str = None) -> str:
        """
        ذخیره نتایج بک تست
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"backtest_results_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
            
        return filename

# مثال استفاده از بک تستر
if __name__ == "__main__":
    backtester = Backtester()
    
    # لیست سیم‌بال‌ها برای آزمایش
    symbols = ["BTC", "ETH", "BNB"]
    
    print("Starting advanced trading backtest...")
    results = backtester.compare_strategies(symbols, days=7)
    
    # نمایش نتایج
    for symbol, data in results.items():
        print(f"\n--- {symbol} ---")
        print(f"Strategy: {data['strategy']}")
        print(f"Initial Balance: {data['initial_balance']:,}")
        print(f"Final Balance: {data['final_balance']:,}")
        print(f"Total Trades: {data['total_trades']}")
        print(f"Profit Percentage: {data['profit_percentage']}%")
        print(f"Total Profit: {data['total_profit']:,}")
        
    # ذخیره نتایج
    filename = backtester.save_results(results)
    print(f"\nResults saved to {filename}")