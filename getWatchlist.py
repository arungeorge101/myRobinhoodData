import json
import datetime
import requests
import collections
import tablib

from collections import defaultdict

# update this token with your personal token
authToken = ""

def getWatchList():
    r = requests.get("https://api.robinhood.com/watchlists/Default/", headers={"authority": "api.robinhood.com", "authorization": "Bearer " + str(
        authToken), "accept": "*/*", "referer": "https://robinhood.com/", "accept-language": "en-US,en;q=0.9", "x-robinhood-api-version": "1.315.0"})

    with open('watchlist.json', 'w') as outfile:
        json.dump(r.json()["results"], outfile)

    while True:

        if(r.json()["next"] is None):
            break

        r = requests.get(r.json()["next"], headers={"authority": "api.robinhood.com", "authorization": "Bearer " + str(
            authToken), "accept": "*/*", "referer": "https://robinhood.com/", "accept-language": "en-US,en;q=0.9", "x-robinhood-api-version": "1.315.0"})
        with open("watchlist.json", "r+") as file:
            data = json.load(file)
            data.extend(r.json()["results"])
            file.seek(0)
            json.dump(data, file)


getWatchList()

with open('watchlist.json') as watchListFile:
    watchListJson = json.load(watchListFile)

watchExcelTranData = tablib.Dataset(title="List")
watchExcelTranData.headers = ['Ticker', 'Date']

watchSummaryData = tablib.Dataset(title="Summary")
watchSummaryData.headers = ['Ticker']

for watch in watchListJson:
    instrumentResponse = requests.get(watch["instrument"])
    instrumentJSON = instrumentResponse.json()

    watchExcelTranData.append([instrumentJSON["symbol"], watch["created_at"]])

watchListExcelBook = tablib.Databook((watchExcelTranData, watchSummaryData))

with open('watchlistdata.xls', 'wb') as watchlistExcelFile:
    watchlistExcelFile.write(watchListExcelBook.export('xls'))