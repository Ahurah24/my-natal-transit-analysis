from strategies.base_strategy import BaseStrategy
from typing import Dict, List, Tuple
import random

class P2PStrategy(BaseStrategy):
    def __init__(self):
        super().__init__()
        self.name = "P2P_Strategy"
        
    def evaluate_signal(self, indicators: Dict) -> Tuple[str, float]:
        """
        ارزیابی سیگنال معاملاتی برای معاملات پیشرفته (P2P)
        با استفاده از اندیکاتورها و شرایط خاص P2P
        """
        signal = "hold"
        strength = 0.0
        
        # شرایط سیگنال خرید
        if self._buy_signal(indicators):
            signal = "buy"
            strength = self._calculate_strength(indicators, "buy")
            
        # شرایط سیگنال فروش
        elif self._sell_signal(indicators):
            signal = "sell"
            strength = self._calculate_strength(indicators, "sell")
        
        return signal, strength
    
    def _buy_signal(self, indicators: Dict) -> bool:
        """
        بررسی شرایط سیگنال خرید
        """
        # RSI کمتر از 30 (فروش بیش از حد)
        if "rsi" in indicators and indicators["rsi"] < 30:
            return True
            
        # MACD crossing above signal line (Buy signal)
        if ("macd" in indicators and "signal" in indicators and 
            indicators["macd"] > indicators["signal"]):
            return True
            
        # قیمت در پایین‌ترین باند بولینگر است
        if ("bb_lower" in indicators and "bb_middle" in indicators and 
            indicators["bb_lower"] < indicators["bb_middle"]):
            return True
            
        return False
    
    def _sell_signal(self, indicators: Dict) -> bool:
        """
        بررسی شرایط سیگنال فروش
        """
        # RSI بیشتر از 70 (خرید بیش از حد)
        if "rsi" in indicators and indicators["rsi"] > 70:
            return True
            
        # MACD crossing below signal line (Sell signal)
        if ("macd" in indicators and "signal" in indicators and 
            indicators["macd"] < indicators["signal"]):
            return True
            
        # قیمت در بالاترین باند بولینگر است
        if ("bb_upper" in indicators and "bb_middle" in indicators and 
            indicators["bb_upper"] > indicators["bb_middle"]):
            return True
            
        return False
    
    def _calculate_strength(self, indicators: Dict, direction: str) -> float:
        """
        محاسبه قدرت سیگنال بر اساس شرایط مختلف
        """
        strength = 0.0
        
        if direction == "buy":
            # محاسبه قدرت خرید
            if "rsi" in indicators:
                rsi_strength = (30 - indicators["rsi"]) / 30 * 100
                strength += rsi_strength
                
            if ("macd" in indicators and "signal" in indicators):
                macd_diff = indicators["macd"] - indicators["signal"]
                macd_strength = min(50, abs(macd_diff) * 10)
                strength += macd_strength
                
        elif direction == "sell":
            # محاسبه قدرت فروش
            if "rsi" in indicators:
                rsi_strength = (indicators["rsi"] - 70) / 30 * 100
                strength += rsi_strength
                
            if ("macd" in indicators and "signal" in indicators):
                macd_diff = indicators["signal"] - indicators["macd"]
                macd_strength = min(50, abs(macd_diff) * 10)
                strength += macd_strength
        
        return min(strength, 100.0)
    
    def get_position_size(self, balance: float, price: float, strength: float) -> float:
        """
        محاسبه اندازه موقعیت بر اساس قدرت سیگنال و موجودی
        """
        # استفاده از قدرت سیگنال در محاسبه اندازه موقعیت
        base_size = balance * 0.05  # 5% از موجودی
        
        if strength > 70:
            # سیگنال قوی - استفاده از 10% از موجودی
            position_size = balance * 0.10
        elif strength > 40:
            # سیگنال متوسط - استفاده از 7% از موجودی
            position_size = balance * 0.07
        else:
            # سیگنال ضعیف - استفاده از 3% از موجودی
            position_size = balance * 0.03
        
        # محدود کردن اندازه موقعیت به حداکثر مجاز
        max_position = balance * 0.1  # حداکثر 10% از موجودی
        return min(position_size, max_position) / price