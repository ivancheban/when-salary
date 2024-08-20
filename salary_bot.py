import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext, ContextTypes
from datetime import datetime, timedelta
import pytz
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

TOKEN = '7220529126:AAH7FUyEW7INpuNr_xe_gohNo3rVCrfQh8A'
CHAT_ID = '-1581609986'  # Replace this with your telegram group chat ID

KYIV_TZ = pytz.timezone('Europe/Kyiv')

def is_ukrainian_holiday(date):
    return False

def get_next_salary_date(current_date):
    # (Existing code to determine the next salary date)

def format_salary_details(next_salary):
    now = datetime.now(KYIV_TZ)
    difference = next_salary - now
    days = difference.days
    hours, remainder = divmod(difference.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    countdown_text = f"{days}d {hours}h {minutes}m {seconds}s"
    next_salary_text = f"Next Salary: {next_salary.strftime('%B %d, %Y')}"
    return f"Time until next salary: {countdown_text}\n{next_salary_text}"

async def scheduled_salary_info(context: ContextTypes.DEFAULT_TYPE):
    now = datetime.now(KYIV_TZ)
    next_salary = get_next_salary_date(now)
    message = format_salary_details(next_salary)
    await context.bot.send_message(chat_id=CHAT_ID, text=message)

def main() -> None:
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("when_salary", when_salary))

    # Create scheduler to run daily at a specific time (e.g., 9:00 AM Kyiv time)
    scheduler = AsyncIOScheduler()
    scheduler.add_job(scheduled_salary_info, 'cron', hour=11, minute=26, timezone=KYIV_TZ, args=[application])
    scheduler.start()

    application.run_polling()

if __name__ == '__main__':
    main()