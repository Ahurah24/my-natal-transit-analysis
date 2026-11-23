    def get_trade_recommendation(self, klines: List[Dict]) -> Dict:
        """
        دریافت توصیه معاملاتی
        """
        try:
            df = self.calculate_indicators(klines)
            
            if len(df) < 2:
                return {
                    'recommendation': 'hold',
                    'confidence': 0,
                    'signals': []
                }
            
            current_index = len(df) - 1
            
            # بررسی سیگنال‌های خرید و فروش
            buy_signal, buy_reason = self.should_buy(df, current_index)
            sell_signal, sell_reason = self.should_sell(df, current_index)
            
            signals_info = {
                'buy_signals': buy_reason,
                'sell_signals': sell_reason
            }
            
            # تعیین توصیه نهایی
            if buy_signal and not sell_signal:
                recommendation = 'buy'
                confidence = min(1.0, (df.iloc[current_index]['RSI'] / 100) * 2)
            elif sell_signal and not buy_signal:
                recommendation = 'sell'
                confidence = min(1.0, (1 - df.iloc[current_index]['RSI'] / 100) * 2)
            else:
                recommendation = 'hold'
                confidence = 0
            
            return {
                'recommendation': recommendation,
                'confidence': float(confidence),
                'signals': signals_info
            }
            
        except Exception as e:
            logger.error(f"Error in trade recommendation: {str(e)}")
            return {
                'recommendation': 'hold',
                'confidence': 0,
                'signals': []
            }

# نمونه استفاده
if __name__ == "__main__":
    strategy = AdvancedTradingStrategy()
    
    # مثال داده‌های کندله (در عمل از API دریافت می‌شوند)
    sample_klines = [
        {'timestamp': 1609459200000, 'open': 100, 'high': 110, 'low': 95, 'close': 105, 'volume': 1000},
        {'timestamp': 1609462800000, 'open': 105, 'high': 115, 'low': 100, 'close': 110, 'volume': 1200},
        # ... بقیه داده‌ها
    ]
    
    recommendation = strategy.get_trade_recommendation(sample_klines)
    print(f"Trade Recommendation: {recommendation}")