#!/usr/bin/env python
"""Class to interact with the Robinhood API and export data."""

import json
import requests
import tablib

from helpers.rh_api_helper import RHApiHelper
from domain.option import Option
from domain.stock import Stock

class RHDataCollector:
    """Class to interact with the Robinhood API and export data.
    """
    def __init__(self):
        self.rhApihelper = RHApiHelper()

    def get_watchlist(self):
        """Get a user's watchlist.

        Returns:
            list: List of objects returned from the "results" section of these calls.
        """
        return self.rhApihelper.api_get_paginated_results("https://api.robinhood.com/watchlists/Default/")

    def get_order_history(self):
        """Get a user's order history.

        Returns:
            list: List of objects returned from the "results" section of these calls.
        """
        return self.rhApihelper.api_get_paginated_results("https://api.robinhood.com/orders/")

    def get_options_history(self):
        """Get a user's options order history.

        Returns:
            list: List of objects returned from the "results" section of these calls.
        """
        return self.rhApihelper.api_get_paginated_results("https://api.robinhood.com/options/orders/")


    def export_watchlist_data(self, fileformat="xls"):
        """Retrieve a user's watchlist data and save as JSON and transposed HTML files.

        Args:
            fileformat (string): Requested file format to export data to, default XLS.
        """
        watchlist = self.get_watchlist()
        self.rhApihelper.save_to_json_file(watchlist, "watchlist")

        # Extract only the Symbol and the Created_At fields from our Watchlist data.
        watchlist_tablerows = []
        for watch_entry in watchlist:
            watch_entry_instrument = self.rhApihelper.api_get(watch_entry["instrument"])
            watchlist_tablerows.append([
                watch_entry_instrument["symbol"],
                watch_entry["created_at"]
            ])

        self.rhApihelper.save_dataset_to_file(
            "watchlistdata",
            fileformat,
            "List",
            ['Ticker', 'Date'],
            watchlist_tablerows
        )

    def export_options_data(self, fileformat="xls"):
        """Retrieve a user's options data and save as JSON and transposed requested file format.

        Args:
            fileformat (string): Requested file format to export data to, default XLS.
        """
        options_history = self.get_options_history()
        self.rhApihelper.save_to_json_file(options_history, "options")

        # Rearrange option fields for our Options data.
        options_tablerows = []

        #Create the excel dataset and headers
        optionsExcelTranData = tablib.Dataset(title="Transactions")
        optionsExcelTranData.headers = ['Ticker', 'Date', 'Quantity', 'Price', 'TranType', 'Total']

        optionsDict = {}

        for option_entry in options_history:
            if option_entry["state"] not in ["cancelled", "confirmed", "rejected"]:
                option = Option()
                
                option.ticker = option_entry["chain_symbol"]
                option.price = option_entry["price"]
                option.totalPrice = option_entry["processed_premium"]
                option.quantity = option_entry["processed_quantity"]
                option.date = option_entry["legs"][0]["executions"][0]["settlement_date"]
                option.tranType = option_entry["legs"][0]["side"]

                optionsExcelTranData.append([option.ticker, option.date, option.quantity, option.price, option.tranType, option.totalPrice])

                # group the stocks into dictionary for further processing
                if option.ticker not in optionsDict:
                    optionsDict[option.ticker] = [option]
                else:
                    optionsDict[option.ticker].append(option)
        
        optionsSummaryData = self.create_summary(optionsDict)

        optionsExcelBook = tablib.Databook((optionsExcelTranData, optionsSummaryData))

        self.rhApihelper.save_dataset_to_excel(
            "optionsdata",
            fileformat,
            optionsExcelBook
        )

    def export_stock_data(self, fileformat="xls"):
        """Retrieve a user's options data and save as JSON and transposed requested file format.

        Args:
            fileformat (string): Requested file format to export data to, default XLS.
        """
        order_history = self.get_order_history()
        self.rhApihelper.save_to_json_file(order_history, "orders")

        stockTranData = tablib.Dataset(title="Transactions")
        stockTranData.headers = ['Ticker', 'Name', 'Date', 'Quantity', 'Price', 'TranType', 'Fees', 'Total']

        stockDict = {}

        for order_entry in order_history:
            if order_entry["state"] not in ["cancelled", "confirmed", "rejected"]:
                order_entry_instrument = self.rhApihelper.api_get(order_entry["instrument"])

                stock = Stock()
                stock.name = order_entry_instrument["simple_name"]
                stock.ticker = order_entry_instrument["symbol"]
                stock.fees = order_entry["fees"]
                stock.price = order_entry["average_price"]
                stock.totalPrice = order_entry["executed_notional"]["amount"]
                stock.quantity = order_entry["cumulative_quantity"]
                stock.date = order_entry["executions"][0]["settlement_date"]
                stock.tranType = order_entry["side"]

                stockTranData.append([stock.ticker, stock.name, stock.date, stock.quantity, stock.price, stock.tranType, stock.fees, stock.totalPrice])

                # Group the stocks into dictionary for further processing.
                if order_entry_instrument["symbol"] not in stockDict:
                    stockDict[stock.ticker] = [stock]
                else:
                    stockDict[stock.ticker].append(stock)

        stockSummaryData = self.create_summary(stockDict)

        stockExcelBook = tablib.Databook((stockTranData, stockSummaryData))

        self.rhApihelper.save_dataset_to_excel(
            "stockdata",
            fileformat,
            stockExcelBook
        )
    
    def create_summary(self, dataDict):
        """Create options/stocks summary data. 

        Args:
            dataDict (dictionary): The dictionary consisting of all the options/stocks data

        Returns:
            tablib.Dataset: returns the summary tablib dataset
        """

        summaryData = tablib.Dataset(title="Summary")
        summaryData.headers = ['Ticker', 'Quantity Bought', 'Total Cost', 'Quantity Sold', 'Total Sale', 'Profit', 'Quantity in hand']

        # process the stocks in the dictionary and calculate P&L
        for key, optionList in dataDict.items():
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
                if(option.tranType == "buy"):
                    totalBought += float(option.quantity)
                    totalCost += float(option.totalPrice)
                elif (option.tranType == "sell"):
                    totalSold += float(option.quantity)
                    totalSale += float(option.totalPrice)
            
            quantLeft = totalBought - totalSold
            profit = totalSale - totalCost

            summaryData.append([option.ticker, totalBought, totalCost, totalSold, totalSale, profit, quantLeft])
        
        return summaryData