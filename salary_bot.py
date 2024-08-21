import logging
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext
from datetime import datetime, timedelta
import pytz
import schedule
import time

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
    # Your existing get_next_salary_date function
    # ...

async def when_salary(update: Update, context: CallbackContext) -> None:
    now = datetime.now(KYIV_TZ)
    next_salary = get_next_salary_date(now)
    difference = next_salary - now

    days = difference.days
    hours, remainder = divmod(difference.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    countdown_text = f"{days}d {hours}h {minutes}m {seconds}s"
    next_salary_text = f"Next Salary: {next_salary.strftime('%B %d, %Y')}"

    await update.message.reply_text(f"Time until next salary: {countdown_text}\n{next_salary_text}")

async def publish_salary_info(context: CallbackContext) -> None:
    now = datetime.now(KYIV_TZ)
    next_salary = get_next_salary_date(now)
    difference = next_salary - now

    days = difference.days
    hours, remainder = divmod(difference.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    countdown_text = f"{days}d {hours}h {minutes}m {seconds}s"
    next_salary_text = f"Next Salary: {next_salary.strftime('%B %d, %Y')}"

    # Replace 'your_telegram_group_id' with the actual group ID you want to send the message to
    await context.bot.send_message(chat_id='-1581609986', text=f"Time until next salary: {countdown_text}\n{next_salary_text}")

def main() -> None:
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("when_salary", when_salary))

    # Schedule the publish_salary_info function to run at 10:30 AM every day
    schedule.every().day.at("13:44").do(lambda: application.run_task(publish_salary_info))

    # Bind to the port provided by Heroku
    application.run_polling()

    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == '__main__':
    main()