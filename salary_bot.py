import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext
from datetime import datetime, timedelta
import pytz
from apscheduler.schedulers.asyncio import AsyncIOScheduler

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = os.getenv('TOKEN')
KYIV_TZ = pytz.timezone('Europe/Kyiv')
CHAT_ID = '-1001581609986'

def easter_date(year):
    a = year % 19
    b = year // 100
    c = year % 100
    d = b // 4
    e = b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i = c // 4
    k = c % 4
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    month = (h + l - 7 * m + 114) // 31
    day = ((h + l - 7 * m + 114) % 31) + 1
    return datetime(year, month, day, tzinfo=KYIV_TZ)

def is_ukrainian_holiday(date):
    year = date.year
    easter = easter_date(year)

    fixed_holidays = [
        (1, 1),   # New Year's Day
        (1, 7),   # Orthodox Christmas
        (3, 8),   # International Women's Day
        (5, 1),   # Labour Day
        (5, 9),   # Victory Day
        (6, 28),  # Constitution Day
        (8, 24),  # Independence Day
        (10, 14), # Defender of Ukraine Day
        (12, 25), # Catholic Christmas
    ]

    variable_holidays = [
        easter - timedelta(days=2),                    # Good Friday
        easter + timedelta(days=1),                    # Easter Monday
        easter + timedelta(days=49),                   # Trinity Sunday
        datetime(year, 5, 1, tzinfo=KYIV_TZ).replace(day=1) + timedelta(days=7 - datetime(year, 5, 1).weekday()), # Day of Memory and Reconciliation (first Sunday of May)
        datetime(year, 10, 1, tzinfo=KYIV_TZ).replace(day=1) + timedelta(days=(6 - datetime(year, 10, 1).weekday()) % 7), # Teacher's Day (first Sunday of October)
    ]

    return (date.month, date.day) in fixed_holidays or date in variable_holidays

def get_next_salary_date(current_date):
    year, month = current_date.year, current_date.month
    if month in [3, 6, 9, 12]:  # Quarter end
        next_salary = datetime(year, month, 1, tzinfo=KYIV_TZ) + timedelta(days=32)
        next_salary = next_salary.replace(day=1) - timedelta(days=1)
    else:
        next_salary = datetime(year, month, 5, tzinfo=KYIV_TZ)
        if current_date > next_salary:
            next_salary = next_salary.replace(month=month+1)

    while next_salary.weekday() >= 5 or is_ukrainian_holiday(next_salary):
        next_salary -= timedelta(days=1)
    
    return next_salary

async def send_salary_countdown(context: CallbackContext, chat_id: str) -> None:
    try:
        now = datetime.now(KYIV_TZ)
        next_salary = get_next_salary_date(now)
        difference = next_salary - now

        days = difference.days
        hours, remainder = divmod(difference.seconds, 3600)
        minutes, _ = divmod(remainder, 60)

        countdown_text = f"{days}d {hours}h {minutes}m"
        next_salary_text = f"Next Salary: {next_salary.strftime('%B %d, %Y')}"

        await context.bot.send_message(chat_id=chat_id, text=f"Time until next salary: {countdown_text}\n{next_salary_text}")
    except Exception as e:
        logger.error(f"Failed to send message: {str(e)}")

def main():
    application = Application.builder().token(TOKEN).build()

    scheduler = AsyncIOScheduler()
    scheduler.add_job(send_salary_countdown, 'cron', hour=16, minute=39, args=[application, CHAT_ID], timezone=KYIV_TZ)
    scheduler.start()

    application.run_polling()

if __name__ == '__main__':
    main()