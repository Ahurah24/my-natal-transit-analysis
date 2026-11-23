    def _calculate_macd(self, prices: List[float], fast: int = 12, slow: int = 26, signal: int = 9) -> Tuple[float, float]:
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
    
    def _calculate_bbands(self, prices: List[float], period: int = 20, std_dev: int = 2) -> Tuple[float, float, float]:
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
    
    def should_buy(self, indicators: Dict, current_price: float, previous_price: float) -> bool:
        """
        تعیین آیا معامله خرید انجام شود یا نه
        """
        # استراتژی پیشرفته با کارمزد صفر و P2P
        if indicators.get("rsi", 50) < 30:  # RSI زیر 30 - معاملات خرید
            return True
            
        if indicators.get("macd", 0) > indicators.get("signal", 0):  # MACD بالای سیگنال
            return True
            
        # بررسی قیمت نسبت به Bollinger Bands
        bb_upper = indicators.get("bb_upper", 0)
        bb_lower = indicators.get("bb_lower", 0)
        
        if current_price <= bb_lower and previous_price > bb_lower:
            return True
            
        return False
    
    def calculate_profit(self, entry_price: float, exit_price: float, quantity: float) -> Dict:
        """
        محاسبه سود معاملات با استفاده از معاملات پیشرفته (کارمزد صفر)
        """
        if entry_price <= 0:
            return {"error": "Invalid entry price"}
            
        profit = ((exit_price - entry_price) / entry_price) * 100
        absolute_profit = (exit_price - entry_price) * quantity
        
        return {
            "profit_percentage": round(profit, 2),
            "absolute_profit": round(absolute_profit, 4),
            "entry_price": entry_price,
            "exit_price": exit_price,
            "quantity": quantity,
            "timestamp": datetime.now().isoformat()
        }
    
    def execute_advanced_trade(self, symbol: str, price_data: List[float], 
                             initial_balance: float = 1000000) -> Dict:
        """
        اجرای معاملات پیشرفته با استفاده از روش P2P و کارمزد صفر
        """
        if len(price_data) < 2:
            return {"error": "Insufficient data for advanced trading"}
        
        total_trades = 0
        total_profit = 0.0
        trades_history = []
        
        # استفاده از معاملات پیشرفته با کارمزد صفر
        position = None  # 'long' or 'short'
        entry_price = 0.0
        
        for i in range(1, len(price_data)):
            current_price = price_data[i]
            previous_price = price_data[i-1]
            
            # محاسبه اندیکاتورها
            indicators = self.calculate_indicators(price_data[:i+1])
            
            # بررسی شرایط خرید
            if position is None and self.should_buy(indicators, current_price, previous_price):
                position = "long"
                entry_price = current_price
                total_trades += 1
                
            # بررسی شرایط فروش
            elif position == "long" and self.should_sell(indicators, current_price, previous_price):
                if entry_price > 0:
                    profit_data = self.calculate_profit(entry_price, current_price, 1.0)
                    total_profit += profit_data["absolute_profit"]
                    
                    trades_history.append({
                        "trade_id": len(trades_history) + 1,
                        "type": "BUY_SELL",
                        "entry_price": entry_price,
                        "exit_price": current_price,
                        "profit_percentage": profit_data["profit_percentage"],
                        "timestamp": datetime.now().isoformat(),
                        "strategy": self.name
                    })
                
                position = None
        
        # محاسبه نرخ بهره کلی
        if price_data:
            initial_price = price_data[0]
            final_price = price_data[-1]
            profit_percentage = ((final_price - initial_price) / initial_price) * 100
            
            return {
                "symbol": symbol,
                "initial_balance": initial_balance,
                "final_balance": initial_balance + total_profit,
                "total_trades": total_trades,
                "profit_percentage": round(profit_percentage, 2),
                "total_profit": round(total_profit, 4),
                "strategy": self.name,
                "advanced_trading_type": "P2P/Advanced",
                "zero_fee_support": True,
                "indicators": indicators,
                "trades_history": trades_history,
                "timestamp": datetime.now().isoformat()
            }
        else:
            return {"error": "Insufficient data for calculation"}