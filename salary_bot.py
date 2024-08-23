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

def easter(year):
    # This is a simplified method to calculate Easter date
    # For production use, consider using a more accurate algorithm or library
    a = year % 19
    b = year // 100
    c = year % 100
    d = (19 * a + b - b // 4 - ((b - (b + 8) // 25 + 1) // 3) + 15) % 30
    e = (32 + 2 * (b % 4) + 2 * (c // 4) - d - (c % 4)) % 7
    f = d + e - 7 * ((a + 11 * d + 22 * e) // 451) + 114
    month = f // 31
    day = f % 31 + 1
    return datetime(year, month, day, tzinfo=KYIV_TZ)

def is_ukrainian_holiday(date):
    # List of fixed Ukrainian public holidays
    fixed_holidays = [
        (1, 1),   # New Year's Day
        (3, 8),   # International Women's Day
        (5, 1),   # International Workers' Day
        (5, 8),   # Day of Remembrance and Victory over Nazism in World War II
        (6, 28),  # Constitution Day
        (7, 15),  # Statehood Day (since 2023)
        (8, 24),  # Independence Day
        (10, 1),  # Defenders of Ukraine Day (since 2023)
        (12, 25), # Christmas
    ]

    # Check if the date is a fixed holiday
    if (date.month, date.day) in fixed_holidays:
        return True

    # Calculate Easter and Pentecost for the given year
    easter_date = easter(date.year)
    pentecost_date = easter_date + timedelta(days=49)

    # Check if the date is Easter or Pentecost
    if date.date() in [easter_date.date(), pentecost_date.date()]:
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
            if month == 12:
                next_salary = datetime(year + 1, 1, 5, tzinfo=KYIV_TZ)
            else:
                next_salary = datetime(year, month + 1, 5, tzinfo=KYIV_TZ)
        
        quarter_end_months = [3, 6, 9, 12]
        if next_salary.month in quarter_end_months:
            next_salary = datetime(next_salary.year, next_salary.month, 1, tzinfo=KYIV_TZ) + timedelta(days=32)
            next_salary = next_salary.replace(day=1) - timedelta(days=1)
        
        while next_salary.weekday() >= 5 or is_ukrainian_holiday(next_salary):
            next_salary -= timedelta(days=1)
    
    return next_salary

def get_salary_message(now, next_salary):
    difference = next_salary - now
    days = difference.days
    hours, remainder = divmod(difference.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    if days == 0 and hours == 0 and minutes == 0:
        return "🎉🎊 It's Salary Day! 💰💸 Enjoy your well-earned money! 🥳🍾"
    elif days == 1:
        return "⏰ Only 1 day left until Salary Day! 💰 Get ready to celebrate! 🎉"
    elif days == 2:
        return "🗓 2 days to go until Salary Day! 💼 The wait is almost over! 😊"
    elif days == 3:
        return "📅 3 days remaining until Salary Day! 💰 It's getting closer! 🙌"
    else:
        countdown_text = f"{days}d {hours}h {minutes}m {seconds}s"
        next_salary_text = f"Next Salary: {next_salary.strftime('%B %d, %Y')}"
        return f"⏳ Time until next salary: {countdown_text}\n📆 {next_salary_text}"

async def when_salary(update: Update, context: CallbackContext) -> None:
    now = datetime.now(KYIV_TZ)
    next_salary = get_next_salary_date(now)
    message = get_salary_message(now, next_salary)
    await update.message.reply_text(message)

async def daily_salary_notification(context: CallbackContext, chat_id: str) -> None:
    try:
        logger.info("Executing scheduled job...")
        now = datetime.now(KYIV_TZ)
        next_salary = get_next_salary_date(now)
        message = get_salary_message(now, next_salary)

        response = await context.bot.send_message(chat_id=chat_id, text=message)
        logger.info(f"Message sent with message id {response.message_id}")
    except Exception as e:
        logger.error(f"Failed to send message: {str(e)}")

def main():
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("when_salary", when_salary))

    scheduler = AsyncIOScheduler()
    scheduler.add_job(daily_salary_notification, 'cron', hour=10, minute=30, args=[application, '-1001581609986'], timezone=KYIV_TZ)
    scheduler.start()

    application.run_polling()

if __name__ == '__main__':
    main()