from urllib import request
from bs4 import BeautifulSoup
import datetime
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools

scopes = 'https://www.googleapis.com/auth/calendar' # For google authentication
product_url = "https://www.saq.com/page/en/saqcom/whisky-canadien/jp-wisers-edition-unique-guy-lafleur/13909547" # Product to notify
test_url = "https://www.saq.com/page/en/saqcom/canadian-whisky/canadian-club-premium/42" # Canadian Club for QA

def make_soup(url):
	"""Generates soup object with given url."""
	res = request.urlopen(url)
	html = res.read()
	soup = BeautifulSoup(html, "lxml")
	return soup

	
def check_availability(url):
	"""Check the SAQ website if item is completely unavailable, how much stock is available online, and if it's available in store"""
	soup = make_soup(url)
	# product-page-avert-colRight only appears on pages where item is totally unavailable
	# If list is not empty, then it's not available
	if len(soup.find_all("div", {"class": "product-page-avert-colRight"})) != 0:
		OutOfStock = True
	else:
		OutOfStock = False
	
	# Get current stock currently for sale
	if len(soup.find_all("div", class_="product-add-to-cart-inventory")) > 1:
		online_quantity_iterator = soup.find_all("div", class_="product-add-to-cart-inventory")[0].stripped_strings
		online_quantity_iterator.__next__()
		OnlineQuantity = online_quantity_iterator.__next__()  # Stock is always second item in iterator
	elif soup.find_all("span", alt="This product is not available online") == 1:  # Not available online when list is one item
		OnlineQuantity = "Unavailable online"
	else: 
		OnlineQuantity = 0  # catch-all for edge cases
	
	# Check if product is completely unavailable in stores
	if len(soup.find_all("span", title="This product is not available in outlets")) != 0:
		InStore = "No"
	else:
		InStore = "Yes"
	
	# Name of beverage
	DrinkName = soup.find_all("h1", {"class": "product-description-title"})[0].string
	
	return [OutOfStock, DrinkName, OnlineQuantity, InStore]


def notify(description, DrinkName, StartTime, EndTime):
	"""Create a Google Calendar event at the specified time, with the specified drink name and description"""
	# The file token.json stores the user's access and refresh tokens, and is
	# created automatically when the authorization flow completes for the first
	# time.
	store = file.Storage('token.json')
	creds = store.get()
	if not creds or creds.invalid:
		flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
		creds = tools.run_flow(flow, store)
	service = build('calendar', 'v3', http=creds.authorize(Http()))

	# Create Event
	event = {
		'summary': f'{DrinkName} is in stock',
		'description': description,
		'start': {
			'dateTime': StartTime,
			'timeZone': 'America/New_York',
		},
		'end': {
			'dateTime': EndTime,
			'timeZone': 'America/New_York',
		},
		'reminders': {
			'useDefault': False,
			'overrides': [
				{'method': 'email', 'minutes': 1},  # Reminder sent 1min before event start
			],
		},
	}
	
	# Send event to Google Calendar
	event = service.events().insert(calendarId='primary', body=event).execute()
	
def main():
	stock_status = check_availability(product_url)
	
	# If drink is not completely unavailable, create event 1 minute in the future
	# Email reminder in notify() is set to one minute before, sending email immediately
	if stock_status[0] is False:
		if stock_status[2] == 0 and stock_status[3] == "No":
			print("Not in stock in store or online")
		else:
			desc = f'Quantity Available Online: {stock_status[2]}\nAvailable in Store: {stock_status[3]}\nLink: {product_url}'
			drink_name = stock_status[1]
			start = datetime.datetime.now() + datetime.timedelta(minutes=1)
			end = start + datetime.timedelta(minutes=5)
			start_time = f'{start.year}-{start.month}-{start.day}T{start.hour}:{start.minute}:{start.second}'
			end_time = f'{end.year}-{end.month}-{end.day}T{end.hour}:{end.minute}:{end.second}'
			notify(desc, drink_name, start_time, end_time)
			print("Success")
	# No event created if drink is unavailable
	else:
		print("Completely unavailable")
	
if __name__ == '__main__':
	main()
