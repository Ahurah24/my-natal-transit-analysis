"""
ربات معاملات خودکار ارزینجا با استراتژی پیشرفته P2P
"""

import sys
import os
from datetime import datetime

# اضافه کردن مسیر به پکیج‌ها
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import settings
from api.arzinja_api import ArzinjaAPI
from strategy.trading_strategy import TradingStrategy
from trader.trader import Trader

def main():
    print("🚀 ربات معاملات ارزینجا")
    print("=" * 40)
    
    # بررسی وجود فایل .env
    env_file = os.path.join(os.path.dirname(__file__), '.env')
    if not os.path.exists(env_file):
        print("❌ فایل .env پیدا نشد!")
        print("لطفاً فایل .env را ایجاد کرده و اطلاعات API خود را وارد کنید.")
        return
    
    # ایجاد شیء تنظیمات
    settings_obj = settings.settings  # Access the global instance
    
    # ایجاد شیء API
    api = ArzinjaAPI(
        api_url=settings_obj.ARZINJA_API_URL,
        api_key=settings_obj.ARZINJA_API_KEY,
        secret=settings_obj.ARZINJA_SECRET
    )
    
    # ایجاد استراتژی معاملاتی
    strategy = TradingStrategy()
    
    # ایجاد ربات معاملاتی
    trader = Trader(api, strategy)
    
    print("📊 در حال آماده‌سازی برای تست بازگشتی...")
    
    try:
        # اجرای تست بازگشتی
        results = trader.run(symbol="BTC_USDT", is_test_mode=True)
        
        print("\n" + "=" * 50)
        print("🔄 آیا مایل به اجرای معاملات واقعی هستید؟")
        print("=" * 50)
        print("✅ نتایج تست بازگشتی:")
        for key, value in results.items():
            if isinstance(value, float):
                print(f"   {key}: {value:.2f}%")
            else:
                print(f"   {key}: {value}")
        
        # سوال از کاربر
        response = input("\nآیا مایل به اجرای معاملات واقعی هستید؟ (y/n): ").strip().lower()
        
        if response in ['y', 'yes', 'بله']:
            print("🟢 شروع معاملات واقعی...")
            trader.run(symbol="BTC_USDT", is_test_mode=False)
        else:
            print("🛑 معاملات واقعی لغو شد.")
            
    except Exception as e:
        print(f"❌ خطای اجرای ربات: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()