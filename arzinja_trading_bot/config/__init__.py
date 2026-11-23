import os
from dotenv import load_dotenv

# بارگذاری متغیرهای محیطی
load_dotenv()

class Settings:
    # API Configuration
    ARZINJA_API_URL = os.getenv('ARZINJA_API_URL', 'https://api-v2.arzinja.ir/api')
    ARZINJA_API_KEY = os.getenv('ARZINJA_API_KEY')
    ARZINJA_SECRET = os.getenv('ARZINJA_SECRET')
    
    # Trading Configuration
    DEFAULT_SYMBOL = os.getenv('DEFAULT_SYMBOL', 'BTC_USDT')
    TRADE_AMOUNT = float(os.getenv('TRADE_AMOUNT', '0.001'))
    MAX_TRADES_PER_DAY = int(os.getenv('MAX_TRADES_PER_DAY', '100'))
    STOP_LOSS_PERCENTAGE = float(os.getenv('STOP_LOSS_PERCENTAGE', '2.0'))
    TAKE_PROFIT_PERCENTAGE = float(os.getenv('TAKE_PROFIT_PERCENTAGE', '5.0'))
    
    # Backtesting Configuration
    BACKTEST_DAYS = int(os.getenv('BACKTEST_DAYS', '30'))
    INITIAL_BALANCE = float(os.getenv('INITIAL_BALANCE', '1000000'))
    
    # Risk Management
    MAX_RISK_PER_TRADE = float(os.getenv('MAX_RISK_PER_TRADE', '1.0'))  # 1% of balance
    POSITION_SIZE_PERCENTAGE = float(os.getenv('POSITION_SIZE_PERCENTAGE', '50.0'))  # 50% of available funds
    
    # Logging Configuration
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    
    def __init__(self):
        if not self.ARZINJA_API_KEY or not self.ARZINJA_SECRET:
            # Don't raise error here to allow imports for testing, but this will be validated when needed
            pass

# Create a global instance of Settings (but don't validate credentials at import time)
def get_settings():
    """Get settings instance with validation"""
    settings_instance = Settings()
    if not settings_instance.ARZINJA_API_KEY or not settings_instance.ARZINJA_SECRET:
        raise ValueError("API credentials must be set in environment variables")
    return settings_instance

# For backward compatibility, we can create a basic instance for imports
try:
    # This creates the global instance but doesn't validate immediately 
    settings = Settings()
except Exception:
    # If there's an issue during import, still make it available
    pass