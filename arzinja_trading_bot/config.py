"""
تنظیمات ربات معاملاتی ارزینجا
"""

# تنظیمات API
API_BASE_URL = "https://api-v2.arzinja.app/api"
PUBLIC_API_URL = "https://arzinja.info/api-docs"

# اطلاعات حساب کاربری (این اطلاعات باید با استفاده از متغیرهای محیطی یا فایل پنهان وارد شود)
API_KEY = ""
SECRET_KEY = ""

# تنظیمات معاملات
TRADE_AMOUNT = 100000  # مبلغ معامله به تومان
MAX_TRADES_PER_DAY = 50
MIN_PROFIT_PERCENTAGE = 2.0  # حداقل سود درصدی

# تنظیمات تست
BACKTEST_DAYS = 30
SIMULATION_MODE = True  # در حالت آزمایشی

# تنظیمات بازار
SUPPORTED_PAIRS = ["BTC_USDT", "ETH_USDT", "BNB_USDT"]