from pynotifier import Notification
import pathlib
import os
import platform
import requests
import json
import time
import sys

#change the critical exchange rate level here
criticalExchangeLevelToNotify = 30000

#change periodic check time here (in mins)
#minimum should be 3 minutes (because I can't do more than 500 api calls per day!)
periodicCheckTime = 3

#personal api key, please don't give this to anyone
#It wouldn't be dramatic if you do but you know, safety first
alphavantageKey = ''

#the following comments are there if you're interested in how things work

url = "https://www.alphavantage.co/query?"

#message I send to Alpha Vantage
#i.e. it is the request to get the current exchange rate of Bitcoin
data = {
    "function": "CURRENCY_EXCHANGE_RATE",
    "from_currency": "BTC",
    "to_currency": "EUR",
    "apikey": alphavantageKey
    ,
}

#making the desktop messages
#------------------------------------
path = os.path.abspath(sys.argv[0])
#maybe this / should be \ on windows, we'll see...
lastSlash = path.rindex("/")
path = path[:lastSlash + 1] + "icon."
if platform.system() == 'Windows':
    path += "ico"
else:
    path += "png"

def notify(msg):
    Notification(
        title='Bitcoin Updater',
        description=msg,
        icon_path=path, # On Windows .ico is required, on Linux - .png
        duration=5,                              # Duration in seconds
        urgency=Notification.URGENCY_CRITICAL
    ).send()
#------------------------------------

#this is where the magic happens: in this function I make the API-Call in order to get the needed information
#------------------------------------
def getCurrentExchangeRate():
    try:
        response = requests.get(url, params=data)
        currentExchange = response.json()["Realtime Currency Exchange Rate"]["5. Exchange Rate"]
        currentExchange = currentExchange.split(".")[0]
        return currentExchange
    except:
        return -1
#------------------------------------

#add the commas in the numbers
#------------------------------------
def makeReadable(numberString):
    return "{:,}".format(int(numberString))
#------------------------------------

#printing an error message in case the data couldn't be fetched
#------------------------------------
def failedFetchingData():
    print("Failed to fetch data.\nThis could be due to too many API-Calls, so maybe try stopping this script (Ctrl+C) and running it a few minutes later")
    time.sleep(60)
#------------------------------------


#checking the exchange rate for the first time since the script started
#------------------------------------
currentExchange = getCurrentExchangeRate()
while currentExchange == -1:
    failedFetchingData()
    currentExchange = getCurrentExchangeRate()

msg = "Current exchange rate: " + makeReadable(currentExchange) + " €"
if int(currentExchange) < criticalExchangeLevelToNotify:    
    msg += "\nThis is below the critical level of : " + makeReadable(criticalExchangeLevelToNotify) + " €!" 
notify(msg)
#------------------------------------


oldExchange = currentExchange

#loop where I check periodicaly wether the price dropped below the critical level
#------------------------------------
while 1:
    time.sleep(periodicCheckTime * 60)
    currentExchange = getCurrentExchangeRate()
    if currentExchange == -1:
        failedFetchingData()
        continue
    
    if int(currentExchange) < criticalExchangeLevelToNotify and int(oldExchange) >= criticalExchangeLevelToNotify:
        msg = "BTC dropped below the critical level of: " + makeReadable(criticalExchangeLevelToNotify) + " €\nIt is now at: " + makeReadable(currentExchange) + " €"
        notify(msg)

    oldExchange = currentExchange
#------------------------------------
