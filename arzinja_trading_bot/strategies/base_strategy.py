from typing import Dict, List
import math

class BaseStrategy:
    def __init__(self):
        self.name = "Base_Strategy"
    
    def calculate_indicators(self, prices: List[float]) -> Dict:
        """
        محاسبه اندیکاتورهای پایه
        """
        indicators = {}
        
        if len(prices) >= 14:
            # RSI
            rsi = self._calculate_rsi(prices)
            indicators["rsi"] = round(rsi, 2)
        
        if len(prices) >= 26:
            # MACD
            macd_line, signal_line = self._calculate_macd(prices)
            indicators["macd"] = round(macd_line, 4)
            indicators["signal"] = round(signal_line, 4)
        
        if len(prices) >= 20:
            # Bollinger Bands
            bb_upper, bb_middle, bb_lower = self._calculate_bbands(prices)
            indicators["bb_upper"] = round(bb_upper, 4)
            indicators["bb_middle"] = round(bb_middle, 4)
            indicators["bb_lower"] = round(bb_lower, 4)
        
        return indicators
    
    def _calculate_rsi(self, prices: List[float], period: int = 14) -> float:
        """
        محاسبه اندیکاتور RSI (Relative Strength Index)
        """
        if len(prices) < period + 1:
            return 50.0
            
        gains = []
        losses = []
        
        for i in range(1, len(prices)):
            change = prices[i] - prices[i-1]
            if change > 0:
                gains.append(change)
                losses.append(0)
            else:
                gains.append(0)
                losses.append(abs(change))
        
        avg_gain = sum(gains[:period]) / period
        avg_loss = sum(losses[:period]) / period
        
        if avg_loss == 0:
            return 100.0
            
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    def _calculate_macd(self, prices: List[float], fast: int = 12, slow: int = 26, signal: int = 9) -> tuple:
        """
        محاسبه اندیکاتور MACD با استفاده از EMA
        """
        if len(prices) < slow:
            return 0.0, 0.0
            
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
    
    def _calculate_bbands(self, prices: List[float], period: int = 20, std_dev: int = 2) -> tuple:
        """
        محاسبه Bollinger Bands
        """
        if len(prices) < period:
            return 0.0, 0.0, 0.0
            
        # میانگین متحرک
        sma = sum(prices[-period:]) / period
        
        # انحراف معیار
        variance = sum([(x - sma) ** 2 for x in prices[-period:]]) / period
        std_deviation = math.sqrt(variance)
        
        upper_band = sma + (std_dev * std_deviation)
        lower_band = sma - (std_dev * std_deviation)
        
        return upper_band, sma, lower_band