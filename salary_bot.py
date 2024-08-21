import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext
from datetime import datetime, timedelta
import pytz
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# Enable detailed logging
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = '7220529126:AAH7FUyEW7INpuNr_xe_gohNo3rVCrfQh8A'
KYIV_TZ = pytz.timezone('Europe/Kyiv')

def is_ukrainian_holiday(date):
    return False  # Comprehensive holiday checks should be implemented here

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

async def daily_salary_notification(context: CallbackContext, chat_id: str) -> None:
    try:
        logger.info("Executing scheduled job...")
        now = datetime.now(KYIV_TZ)
        next_salary = get_next_salary_date(now)
        difference = next_salary - now

        days = difference.days
        hours, remainder = divmod(difference.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)

        countdown_text = f"{days}d {hours}h {minutes}m {seconds}s"
        next_salary_text = f"Next Salary: {next_salary.strftime('%B %d, %Y')}"

        response = await context.bot.send_message(chat_id=chat_id, text=f"Time until next salary: {countdown_text}\n{next_salary_text}")
        logger.info(f"Message sent with message id {response.message_id}")
    except Exception as e:
        logger.error(f"Failed to send message: {str(e)}")

def main():
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("when_salary", when_salary))

    scheduler = AsyncIOScheduler()
    scheduler.add_job(daily_salary_notification, 'cron', hour=16, minute=35, args=[application, '-1001581609986'], timezone=KYIV_TZ)
    scheduler.start()

    application.run_polling()

if __name__ == '__main__':
    main()