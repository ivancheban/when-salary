import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext
from datetime import datetime, timedelta
import pytz
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# Enable detailed logging
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = os.getenv('TOKEN')
KYIV_TZ = pytz.timezone('Europe/Kyiv')

def is_ukrainian_holiday(date):
    # List of fixed Ukrainian public holidays
    fixed_holidays = [
        (1, 1),   # New Year's Day
        (1, 7),   # Christmas (Orthodox)
        (3, 8),   # International Women's Day
        (5, 1),   # Labour Day
        (5, 9),   # Victory Day
        (6, 28),  # Constitution Day
        (8, 24),  # Independence Day
        (10, 14), # Defender of Ukraine Day
        (12, 25), # Christmas (Western)
    ]

    # Check if the date is a fixed holiday
    if (date.month, date.day) in fixed_holidays:
        return True

    # Easter and related holidays (these dates change each year)
    # You would need to calculate these for each year
    # For simplicity, we'll use 2023 dates as an example
    easter_related_holidays_2023 = [
        datetime(2023, 4, 16, tzinfo=KYIV_TZ),  # Easter
        datetime(2023, 6, 4, tzinfo=KYIV_TZ),   # Trinity Sunday
    ]

    # Check if the date is an Easter-related holiday
    if any(date.date() == holiday.date() for holiday in easter_related_holidays_2023):
        return True

    return False

def get_next_salary_date(current_date):
    year, month, day = current_date.year, current_date.month, current_date.day
    if year < 2024 or (year == 2024 and month < 9) or (year == 2024 and month == 9 and day < 5):
        next_salary = datetime(2024, 9, 5, tzinfo=KYIV_TZ)
    elif year == 2024 and month == 9 and day >= 5:
        next_salary = datetime(2024, 9, 30, tzinfo=KYIV_TZ)
    else:
        next_salary = datetime(year, month, 5, tzinfo=KYIV_TZ)
        if current_date > next_salary:
            next_salary += timedelta(days=30)
        quarter_end_months = [2, 5, 8, 11]
        if next_salary.month in quarter_end_months:
            next_salary = datetime(next_salary.year, next_salary.month + 1, 1, tzinfo=KYIV_TZ) - timedelta(days=1)
        else:
            while next_salary.weekday() >= 5 or is_ukrainian_holiday(next_salary):
                next_salary += timedelta(days=1)
    return next_salary

# ... (rest of the code remains the same)

if __name__ == '__main__':
    main()