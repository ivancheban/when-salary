import logging
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext, JobQueue
from datetime import datetime, timedelta, time
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
    # Function body remains the same
    pass
  
async def when_salary(update: Update, context: CallbackContext) -> None:
    # Function body remains the same
    pass

async def daily_salary_notification(context: CallbackContext) -> None:
    job = context.job
    chat_id = job.context['chat_id']
    now = datetime.now(KYIV_TZ)
    next_salary = get_next_salary_date(now)
    difference = next_salary - now
    days = difference.days
    hours, remainder = divmod(difference.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    countdown_text = f"{days}d {hours}h {minutes}m {seconds}s"
    next_salary_text = f"Next Salary: {next_salary.strftime('%B %d, %Y')}"
    text = f"Time until next salary: {countdown_text}\n{next_salary_text}"
    await context.bot.send_message(chat_id=chat_id, text=text)

def schedule_daily_notification(application: Application, chat_id: str) -> None:
    job_queue = application.job_queue

    # Schedule the task to run daily at a specific time (e.g., 09:00 AM in Kyiv timezone)
    target_time = time(hour=11, minute=57, tzinfo=KYIV_TZ)
    job_queue.run_daily(daily_salary_notification, target_time, context={'chat_id': chat_id})

def main() -> None:
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("when_salary", when_salary))

    chat_id = '-1581609986'  # Provide chat id here
    schedule_daily_notification(application, chat_id)

    application.run_polling()

if __name__ == '__main__':
    main()