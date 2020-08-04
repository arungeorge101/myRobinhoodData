import json
import datetime
import requests
import collections
import tablib

from collections import defaultdict


class Stocks:
    name = ""
    ticker = ""
    price = 0
    totalPrice = 0
    quantity = 0
    fees = 0
    date = ""
    tranType = ""


class Options:
    ticker = ""
    price = 0
    totalPrice = 0
    quantity = 0
    date = ""
    tranType = ""


# update this token with your personal token
authToken = ""


def getOrderHistory():
    r = requests.get("https://api.robinhood.com/orders/", headers={"authority": "api.robinhood.com", "authorization": "Bearer " + str(
        authToken), "accept": "*/*", "referer": "https://robinhood.com/", "accept-language": "en-US,en;q=0.9", "x-robinhood-api-version": "1.315.0"})

    with open('orders.json', 'w') as outfile:
        json.dump(r.json()["results"], outfile)

    while True:

        if(r.json()["next"] is None):
            break

        r = requests.get(r.json()["next"], headers={"authority": "api.robinhood.com", "authorization": "Bearer " + str(
            authToken), "accept": "*/*", "referer": "https://robinhood.com/", "accept-language": "en-US,en;q=0.9", "x-robinhood-api-version": "1.315.0"})
        with open("orders.json", "r+") as file:
            data = json.load(file)
            data.extend(r.json()["results"])
            file.seek(0)
            json.dump(data, file)


def getOptionsHistory():
    r = requests.get("https://api.robinhood.com/options/orders/", headers={"authority": "api.robinhood.com", "authorization": "Bearer " + str(
        authToken), "accept": "*/*", "referer": "https://robinhood.com/", "accept-language": "en-US,en;q=0.9", "x-robinhood-api-version": "1.315.0"})
    print (r.json())

    with open('options.json', 'w') as outfile:
        json.dump(r.json()["results"], outfile)

    while True:

        if(r.json()["next"] is None):
            break

        r = requests.get(r.json()["next"], headers={"authority": "api.robinhood.com", "authorization": "Bearer " + str(
            authToken), "accept": "*/*", "referer": "https://robinhood.com/", "accept-language": "en-US,en;q=0.9", "x-robinhood-api-version": "1.315.0"})
        with open("options.json", "r+") as file:
            data = json.load(file)
            data.extend(r.json()["results"])
            file.seek(0)
            json.dump(data, file)

getOrderHistory()
getOptionsHistory()

with open('options.json') as optionsFile:
    optionsJson = json.load(optionsFile)

optionsExcelTranData = tablib.Dataset(title="Transactions")
optionsExcelTranData.headers = [
    'Ticker', 'Date', 'Quantity', 'Price', 'TranType', 'Total']

optionsDict = {}

for oneOption in optionsJson:
    if(oneOption["state"] != "cancelled" and oneOption["state"] != "confirmed" and oneOption["state"] != "rejected"):
        option = Options()

        option.ticker = oneOption["chain_symbol"]
        option.price = oneOption["price"]
        option.totalPrice = oneOption["processed_premium"]
        option.quantity = oneOption["processed_quantity"]
        option.date = oneOption["legs"][0]["executions"][0]["settlement_date"]
        option.tranType = oneOption["legs"][0]["side"]

        optionsExcelTranData.append(
            [option.ticker, option.date, option.quantity, option.price, option.tranType, option.totalPrice])


         # group the stocks into dictionary for further processing
        if option.ticker not in optionsDict:
            optionsDict[option.ticker] = [option]
        else:
            optionsDict[option.ticker].append(option)

optionsSummaryData = tablib.Dataset(title="Summary")
optionsSummaryData.headers = ['Ticker', 'Quantity Bought', 'Total Cost',
                              'Quantity Sold', 'Total Sale', 'Profit', 'Quantity in hand']

# process the stocks in the dictionary and calculate P&L
'''for key, optionList in optionsDict.iteritems():
    # variables to create the summary data
    totalBought = 0
    totalCost = 0
    totalSold = 0
    totalSale = 0
    profit = 0
    quantLeft = 0

    # sorting the list so that we can get the older transaction first
    optionList.sort(key=lambda x: x.date)

    for option in optionList:
        #optionsExcelTranData.append([option.ticker, option.date, option.quantity,
                              #option.price, option.tranType, option.totalPrice])

        if(option.tranType == "buy"):
            totalBought += float(option.quantity)
            totalCost += float(option.totalPrice)
        elif (option.tranType == "sell"):
            totalSold += float(option.quantity)
            totalSale += float(option.totalPrice)

    print "Summary data for : {}".format(option.ticker)
    print "Total Bought : {}".format(totalBought)
    print "Total Cost : {}".format(totalCost)
    print "Total Sold : {}".format(totalSold)
    print "Total Sale : {}".format(totalSale)

    if(totalBought == totalSold):
        profit = totalSale - totalCost
        quantLeft = 0
    elif (totalSold < totalBought):
        quantLeft = totalBought - totalSold
        profit = totalSale - totalCost

    optionsSummaryData.append([option.ticker, totalBought, totalCost, totalSold, totalSale, profit, quantLeft])'''

optionsExcelBook = tablib.Databook((optionsExcelTranData, optionsSummaryData))

with open('optionsdata.xls', 'wb') as optionsExcelFile:
    optionsExcelFile.write(optionsExcelBook.export('xls'))

with open('orders.json') as OrdersFile:
    ordersJson = json.load(OrdersFile)

stockDict = {}

for order in ordersJson:
    if(order["state"] != "cancelled" and order["state"] != "confirmed" and order["state"] != "rejected"):
        #print (order["instrument"])
        stock = Stocks()

        instrumentResponse = requests.get(order["instrument"])
        instrumentJSON = instrumentResponse.json()
        # print(instrumentJSON)

        stock.name = instrumentJSON["simple_name"]
        stock.ticker = instrumentJSON["symbol"]
        stock.fees = order["fees"]
        stock.price = order["average_price"]
        stock.totalPrice = order["executed_notional"]["amount"]
        stock.quantity = order["cumulative_quantity"]
        stock.date = order["executions"][0]["settlement_date"]
        stock.tranType = order["side"]

        # group the stocks into dictionary for further processing
        if stock.ticker not in stockDict:
            stockDict[stock.ticker] = [stock]
        else:
            stockDict[stock.ticker].append(stock)

excelSummaryData = tablib.Dataset(title="Summary")
excelSummaryData.headers = ['Ticker', 'Quantity Bought', 'Total Cost', 'Avg Cost',
                            'Quantity Sold', 'Total Sale', 'Avg Sale', 'Profit', 'Quantity in hand']
excelTranData = tablib.Dataset(title="Transactions")
excelTranData.headers = ['Ticker', 'Name', 'Date',
                         'Quantity', 'Price', 'TranType', 'Fees', 'Total']

# process the stocks in the dictionary and calculate P&L
for key, stockList in stockDict.iteritems():
    # variables to create the summary data
    totalBought = 0
    totalCost = 0
    avgCost = 0
    totalSold = 0
    totalSale = 0
    avgSale = 0
    profit = 0
    quantLeft = 0

    # sorting the list so that we can get the older transaction first
    stockList.sort(key=lambda x: x.date)

    for stock in stockList:
        excelTranData.append([stock.ticker, stock.name, stock.date, stock.quantity,
                              stock.price, stock.tranType, stock.fees, stock.totalPrice])

        """ if(stock.tranType == "buy"):
            totalBought += float(stock.quantity)
            totalCost += float(stock.totalPrice)
        elif (stock.tranType == "sell"):
            totalSold += float(stock.quantity)
            totalSale += float(stock.totalPrice)

    print "Summary data for : {}".format(stock.ticker)
    print "Total Bought : {}".format(totalBought)
    print "Total Cost : {}".format(totalCost)
    print "Total Sold : {}".format(totalSold)
    print "Total Sale : {}".format(totalSale)

    avgCost = totalCost/totalBought

    if(totalSold > 0):
        avgSale = totalSale/totalSold
    else:
        avgSale = 0

    if(totalBought == totalSold):
        profit = totalSale - totalCost
        quantLeft = 0
    elif (totalSold < totalBought):
        quantLeft = totalBought - totalSold
        profit = totalSale - avgCost * totalSold

    excelSummaryData.append([stock.ticker, totalBought, totalCost,
                             avgCost, totalSold, totalSale, avgSale, profit, quantLeft]) """

    excelBook = tablib.Databook((excelTranData, excelSummaryData))

with open('stockdata.xls', 'wb') as stockFile:
    stockFile.write(excelBook.export('xls'))
