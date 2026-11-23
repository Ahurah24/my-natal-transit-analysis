import logging
from datetime import datetime
from typing import Optional

class Logger:
    def __init__(self, name: str = "ArzinjaBot", log_file: Optional[str] = None):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        
        # اطمینان از عدم اضافه شدن هندلر دوباره
        if not self.logger.handlers:
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            
            # هندلر کنسول
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)
            
            # هندلر فایل اگر مشخص شده باشد
            if log_file:
                file_handler = logging.FileHandler(log_file)
                file_handler.setFormatter(formatter)
                self.logger.addHandler(file_handler)
    
    def info(self, message: str):
        """پیام اطلاعاتی"""
        self.logger.info(message)
    
    def warning(self, message: str):
        """پیام هشدار"""
        self.logger.warning(message)
    
    def error(self, message: str):
        """پیام خطا"""
        self.logger.error(message)
    
    def debug(self, message: str):
        """پیام دیباگ"""
        self.logger.debug(message)

# ایجاد یک نمونه لاگر استاندارد
logger = Logger("ArzinjaBot")