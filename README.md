# Ukrainian Salary Date Calculator Bot

This Telegram bot calculates and notifies users about the next salary date, taking into account Ukrainian public holidays and specific salary rules.

## Features

- Calculates the next salary date based on current date and specific rules.
- Considers Ukrainian public holidays when determining salary dates.
- Provides a countdown to the next salary date.
- Sends daily notifications about the time remaining until the next salary.

## Salary Date Rules

1. Before September 5, 2024:
   - Next salary date is fixed to September 5, 2024

2. For September 2024:
   - If current date is before September 5, next salary is September 5, 2024
   - If current date is September 5 or later, next salary is September 30, 2024

3. After September 2024:
   - For non-quarter-end months:
     - Salary is generally paid on the 5th of each month
   - For quarter-end months (March, June, September, December):
     - Salary is paid on the last day of the month
   - If the salary date (either the 5th or the last day of a quarter-end month) falls on a weekend or public holiday, it's moved to the previous working day

## Ukrainian Public Holidays

The bot considers the following Ukrainian public holidays:

- Fixed dates:
  - January 1: New Year's Day
  - March 8: International Women's Day
  - May 1: International Workers' Day
  - May 8: Day of Remembrance and Victory over Nazism in World War II
  - June 28: Constitution Day
  - July 15: Statehood Day
  - August 24: Independence Day
  - October 1: Defenders of Ukraine Day
  - December 25: Christmas

- Variable dates:
  - Easter Sunday (calculated for each year)
  - Pentecost (49 days after Easter)

## Commands

- `/when_salary`: Provides the time remaining until the next salary and the exact date

## Scheduled Notifications

The bot sends daily notifications at 10:30 (Kyiv time) with the countdown to the next salary date.

## Technical Details

- Built using Python and the python-telegram-bot library
- Uses APScheduler for scheduling daily notifications
- Timezone calculations are done using the pytz library, set to Europe/Kyiv

## Setup

1. Clone the repository
2. Install the required dependencies:

    `pip install python-telegram-bot pytz APScheduler`

3. Set the `TOKEN` environment variable with your Telegram bot token
4. Run the script:

    `python salary_bot.py`

## Note

The calculation of Easter is simplified in this version. For production use, consider implementing a more robust method to calculate this date for each year or use a specialized library.