import logging
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext
from datetime import datetime, timedelta
import pytz

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Your bot token from BotFather
TOKEN = '7220529126:AAH7FUyEW7INpuNr_xe_gohNo3rVCrfQh8A'

# Define Kyiv time zone
KYIV_TZ = pytz.timezone('Europe/Kyiv')

def is_ukrainian_holiday(date):
    # Implement a comprehensive holiday check here
    return False

def get_next_salary_date(current_date):
    year = current_date.year
    month = current_date.month
    day = current_date.day

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

async def when_salary(update: Update, context: CallbackContext) -> None:
    now = datetime.now(KYIV_TZ)
    next_salary = get_next_salary_date(now)
    difference = next_salary - now

    days = difference.days
    hours, remainder = divmod(difference.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    countdown_text = f"{days}d {hours}h {minutes}m {seconds}s"
    next_salary_text = f"Next Salary: {next_salary.strftime('%Y-%m-%d')}"

    await update.message.reply_text(f"Time until next salary: {countdown_text}\n{next_salary_text}")

def main() -> None:
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("when_salary", when_salary))

    # Bind to the port provided by Heroku
    application.run_polling()

if __name__ == '__main__':
    main()
