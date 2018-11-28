# SAQChecker
Check if the SAQ has a drink in stock, run as a cron job or Windows Task Scheduler.

Thrown together to get notification for a potential birthdya gift for a friend.

## Installation
1. Ensure python 3.6 is installed, as the project makes use of f'strings
2. Install from requirements.txt
3. In the project directory, generate a token.json from the instructions <a href="https://developers.google.com/calendar/quickstart/python">here</a>
4. Run Saqchecker.py to generate credentials.json
5. Put the url of the drink you wish to be notified about in product_url in Saqchecker.py
6. Set up on a schedule via cron or windows task scheduler
