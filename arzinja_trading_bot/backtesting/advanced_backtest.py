"""
استراتژی‌های پیشرفته برای تست تاریخچه‌ای
"""

from typing import Dict, List
import math

class AdvancedBacktestStrategy:
    def __init__(self):
        pass
    
    def macd_indicator(self, prices: List[float], fast: int = 12, slow: int = 26, signal: int = 9) -> Tuple[float, float]:
        """
        محاسبه اندیکاتور MACD
        """
        if len(prices) < slow:
            return 0.0, 0.0
            
        # محاسبه EMA
        def ema(values, period):
            if len(values) < period:
                return values[-1] if values else 0.0
                
            multiplier = 2 / (period + 1)
            ema_values = [values[0]]
            
            for i in range(1, len(values)):
                ema_value = (values[i] * multiplier) + (ema_values[-1] * (1 - multiplier))
                ema_values.append(ema_value)
                
            return ema_values[-1]
        
        fast_ema = ema(prices, fast)
        slow_ema = ema(prices, slow)
        
        if slow_ema != 0:
            macd_line = fast_ema - slow_ema
            signal_line = ema([macd_line] * len(prices), signal)
            return macd_line, signal_line
        else:
            return 0.0, 0.0
    
    def run_advanced_strategy_backtest(self, symbol: str, initial_balance: float = 1000000) -> Dict:
        """
        اجرای تست استراتژی پیشرفته با استفاده از معاملات P2P/Advanced
        """
        print(f"Running advanced strategy backtest for {symbol}...")
        
        # در اینجا می‌توانیم از کلاس BacktestEngine داده‌ها را بگیریم
        # اما برای سادگی از اطلاعات مصنوعی استفاده می‌کنیم
        
        try:
            # اینجا یک نمونه ساده از معاملات پیشرفته را شبیه‌سازی می‌کنیم
            import random
            
            # شبیه‌سازی قیمت‌ها برای 100 دوره
            base_price = 50000
            prices = [base_price]
            
            for i in range(1, 100):
                change = random.uniform(-0.02, 0.02)  # تغییر بین -2% تا +2%
                new_price = prices[-1] * (1 + change)
                prices.append(new_price)
            
            # محاسبات پیشرفته برای معاملات P2P/Advanced
            total_profit = 0.0
            trades_made = 0
            
            # استراتژی پیشرفته: معاملات با کارمزد صفر و استفاده از P2P
            for i in range(1, len(prices)):
                current_price = prices[i]
                previous_price = prices[i-1]
                
                # محاسبه تغییر قیمت
                price_change = ((current_price - previous_price) / previous_price) * 100
                
                # استراتژی معاملات پیشرفته (با کارمزد صفر)
                if abs(price_change) > 0.5:  # تغییر بیشتر از 0.5%
                    trades_made += 1
                    profit_per_trade = current_price * 0.001  # سود 0.1% برای هر معامله (بدون کارمزد)
                    total_profit += profit_per_trade
            
            # محاسبه نرخ بهره کلی
            if prices:
                initial_price = prices[0]
                final_price = prices[-1]
                
                # استفاده از معاملات P2P با کارمزد صفر
                profit_percentage = ((final_price - initial_price) / initial_price) * 100
                
                return {
                    "symbol": symbol,
                    "initial_balance": initial_balance,
                    "final_balance": initial_balance * (1 + profit_percentage/100),
                    "profit_percentage": profit_percentage,
                    "total_trades": trades_made,
                    "strategy": "Advanced P2P Trading",
                    "zero_fee_support": True,  # پشتیبانی از کارمزد صفر
                    "advanced_trading_type": "P2P/Advanced",
                    "indicators": {
                        "total_profit": total_profit,
                        "average_price_change": sum([((prices[i] - prices[i-1]) / prices[i-1]) * 100 
                                                  for i in range(1, len(prices))]) / len(prices) if prices else 0
                    },
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {"error": "Insufficient data for advanced backtest"}
                
        except Exception as e:
            print(f"Error in advanced backtest: {e}")
            return {"error": str(e)}

# تست استراتژی
if __name__ == "__main__":
    strategy = AdvancedBacktestStrategy()
    result = strategy.run_advanced_strategy_backtest("BTC_USDT")
    print(result)