        if not data or 'data' not in data:
            logger.error("Failed to load test data")
            return {"error": "Failed to load test data"}
        
        # چاپ اطلاعات مربوط به داده‌ها
        logger.info(f"Loaded {len(data['data']['close'])} data points for backtest")
        
        total_trades = 0
        total_profit = 0.0
        win_count = 0
        loss_count = 0
        
        # اجرای تست بازگشتی
        prices = data['data']['close']
        timestamps = data['data']['timestamp']
        
        if len(prices) < 50:
            logger.warning("Not enough data for backtest")
            return {"error": "Insufficient data for backtest"}
        
        # برای هر نقطه داده، سیگنال ارزیابی کن
        balance_history = [self.balance]
        
        for i in range(50, len(prices)):
            # دریافت 50 عدد آخر قیمت برای محاسبات
            window_prices = prices[max(0, i-50):i+1]
            
            # محاسبه اندیکاتورها
            indicators = self.strategy.calculate_indicators(window_prices)
            
            # ارزیابی سیگنال
            signal, strength = self.strategy.evaluate_signal(indicators)
            
            # اجرای معامله فقط اگر سیگنال وجود داشته باشد
            if signal != "hold":
                total_trades += 1
                
                # محاسبه اندازه موقعیت
                position_size = self.strategy.get_position_size(self.balance, prices[i], strength)
                
                # اجرای معامله (به صورت آزمایشی - فقط تغییر موجودی)
                if signal == "buy":
                    # خرید: کاهش موجودی و افزایش موقعیت
                    cost = position_size * prices[i]
                    self.balance -= cost
                    self.position += position_size
                    
                elif signal == "sell":
                    # فروش: افزایش موجودی و کاهش موقعیت
                    revenue = position_size * prices[i]
                    self.balance += revenue
                    self.position -= position_size
                
                # محاسبه سود/زیان از معاملات
                if i > 0:
                    current_value = self.balance + (self.position * prices[i])
                    previous_value = balance_history[-1] if balance_history else self.balance
                    
                    profit = current_value - previous_value
                    total_profit += profit
                    
                    if profit > 0:
                        win_count += 1
                    elif profit < 0:
                        loss_count += 1
                
                # ذخیره موجودی برای تاریخچه
                balance_history.append(self.balance + (self.position * prices[i]))
        
        # محاسبه نتایج کلی
        final_balance = self.balance + (self.position * prices[-1])
        total_return = ((final_balance - Settings.INITIAL_BALANCE) / Settings.INITIAL_BALANCE) * 100
        
        results = {
            "symbol": symbol,
            "initial_balance": Settings.INITIAL_BALANCE,
            "final_balance": final_balance,
            "total_return_percent": round(total_return, 2),
            "total_trades": total_trades,
            "win_count": win_count,
            "loss_count": loss_count,
            "win_rate": round((win_count / total_trades * 100) if total_trades > 0 else 0, 2),
            "average_profit_per_trade": round(total_profit / total_trades if total_trades > 0 else 0, 2)
        }
        
        logger.info(f"Backtest results for {symbol}:")
        logger.info(f"  Initial Balance: {Settings.INITIAL_BALANCE:,}")
        logger.info(f"  Final Balance: {final_balance:,.0f}")
        logger.info(f"  Total Return: {total_return:.2f}%")
        logger.info(f"  Total Trades: {total_trades}")
        logger.info(f"  Win Rate: {results['win_rate']}%")
        
    def run_live_trading(self, symbol: str):
        """
        اجرای معاملات زنده (در صورت تأیید کاربر)
        """
        logger.info("Starting live trading...")
        
        # دریافت اطلاعات حساب
        account_info = self.api.get_account_info()
        
        if 'error' in account_info:
            logger.error(f"Failed to get account info: {account_info['error']}")
            return
        
        logger.info(f"Account info retrieved successfully")
        logger.info(f"Available balance: {account_info.get('balance', 0):,}")
        
        # دریافت آخرین داده‌های بازار
        market_data = self.api.get_market_data(symbol)
        
        if 'error' in market_data:
            logger.error(f"Failed to get market data: {market_data['error']}")
            return
        
        # اجرای استراتژی و معامله
        prices = market_data['data']['close']
        indicators = self.strategy.calculate_indicators(prices)
        
        signal, strength = self.strategy.evaluate_signal(indicators)
        
        if signal != "hold":
            logger.info(f"Signal detected: {signal} with strength {strength:.2f}%")
            
            # محاسبه اندازه موقعیت
            position_size = self.strategy.get_position_size(
                account_info.get('balance', 0), 
                prices[-1], 
                strength
            )
            
            # اجرای معامله پیشرفته با کارمزد صفر (P2P)
            trade_result = self.api.execute_trade(
                symbol=symbol,
                trade_type=signal,
                amount=position_size,
                price=prices[-1]
            )
            
            if 'error' in trade_result:
                logger.error(f"Trade execution failed: {trade_result['error']}")
            else:
                logger.info(f"Trade executed successfully: {trade_result}")
                
        else:
            logger.info("No trading signal detected")
    
    def run(self, symbol: str = "BTC_USDT", is_test_mode: bool = True):
        """
        اجرای کامل ربات
        """
        logger.info("Starting Arzinja Trading Bot...")
        
        if is_test_mode:
            # اجرای تست بازگشتی
            results = self.run_backtest(symbol)
            
            print("\n" + "="*50)
            print("BACKTEST RESULTS")
            print("="*50)
            for key, value in results.items():
                if isinstance(value, float):
                    print(f"{key}: {value:.2f}")
                else:
                    print(f"{key}: {value}")
            
            return results
        else:
            # اجرای معاملات زنده
            self.run_live_trading(symbol)