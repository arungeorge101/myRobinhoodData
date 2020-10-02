#!/usr/bin/env python
"""Class to interact with the Robinhood API and export data."""

import json
import requests
import tablib

class RobinhoodAPIWrapper:
    """Class to interact with the Robinhood API and export data.
    """
    def __init__(self, auth_token = None):
        self.auth_token = auth_token or get_api_token()

    def api_get(self, request_url):
        """Perform an authenticated GET request against a given Robinhood url.

        Args:
            auth_token (string): Bearer token used for API calls.
            request_url (string): URL to make GET call against.

        Returns:
            dict: Dictionary containing JSON response of call.
        """
        response = requests.get(request_url, headers = {
            "authority"              : "api.robinhood.com",
            "authorization"          : "Bearer " + self.auth_token,
            "accept"                 : "*/*",
            "referer"                : "https://robinhood.com/",
            "accept-language"        : "en-US,en;q=0.9",
            "x-robinhood-api-version": "1.315.0"
        })
        return response.json()

    def api_get_paginated_results(self, paginated_request_url):
        """Call the API and assemble all the "results" if the calls are paginated.

        Args:
            paginated_request_url (string): Starting URL that will return "next" for more calls.

        Returns:
            list: All entries returned from the "results" section of the calls.
        """
        paginated_results = []
        response = self.api_get(paginated_request_url)
        paginated_results += response["results"]
        while response["next"]:
            response = self.api_get(response["next"])
            paginated_results += response["results"]
        return paginated_results

    def get_watchlist(self):
        """Get a user's watchlist.

        Returns:
            list: List of objects returned from the "results" section of these calls.
        """
        return self.api_get_paginated_results("https://api.robinhood.com/watchlists/Default/")

    def get_order_history(self):
        """Get a user's order history.

        Returns:
            list: List of objects returned from the "results" section of these calls.
        """
        return self.api_get_paginated_results("https://api.robinhood.com/orders/")

    def get_options_history(self):
        """Get a user's options order history.

        Returns:
            list: List of objects returned from the "results" section of these calls.
        """
        return self.api_get_paginated_results("https://api.robinhood.com/options/orders/")


    def export_watchlist_data(self, fileformat="xls"):
        """Retrieve a user's watchlist data and save as JSON and transposed HTML files.

        Args:
            fileformat (string): Requested file format to export data to, default XLS.
        """
        watchlist = self.get_watchlist()
        save_to_json_file(watchlist, "watchlist")

        # Extract only the Symbol and the Created_At fields from our Watchlist data.
        watchlist_tablerows = []
        for watch_entry in watchlist:
            watch_entry_instrument = self.api_get(watch_entry["instrument"])
            watchlist_tablerows.append([
                watch_entry_instrument["symbol"],
                watch_entry["created_at"]
            ])

        save_dataset_to_file(
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
        save_to_json_file(options_history, "options")

        # Rearrange option fields for our Options data.
        options_tablerows = []
        for option_entry in options_history:
            if option_entry["state"] in ["cancelled", "confirmed", "rejected"]:
                continue

            options_tablerows.append([
                option_entry["chain_symbol"],                                  # Ticker
                option_entry["legs"][0]["executions"][0]["settlement_date"],   # Date
                option_entry["processed_quantity"],                            # Quantity
                option_entry["price"],                                         # Price
                option_entry["legs"][0]["side"],                               # TranType
                option_entry["processed_premium"]                              # Total
            ])

        save_dataset_to_file(
            "optionsdata",
            fileformat,
            "Transactions",
            ['Ticker', 'Date', 'Quantity', 'Price', 'TranType', 'Total'],
            options_tablerows
        )

    def export_orders_data(self, fileformat="xls"):
        """Retrieve a user's options data and save as JSON and transposed requested file format.

        Args:
            fileformat (string): Requested file format to export data to, default XLS.
        """
        order_history = self.get_order_history()
        save_to_json_file(order_history, "orders")

        stocks_dict = {}
        for order_entry in order_history:
            if order_entry["state"] in ["cancelled", "confirmed", "rejected"]:
                continue

            order_entry_instrument = self.api_get(order_entry["instrument"])

            stock_entry = [
                order_entry_instrument["symbol"],                 # Ticker
                order_entry_instrument["simple_name"],            # Name
                order_entry["executions"][0]["settlement_date"],  # Date
                order_entry["cumulative_quantity"],               # Quantity
                order_entry["average_price"],                     # Price
                order_entry["side"],                              # TranType
                order_entry["fees"],                              # Fees
                order_entry["executed_notional"]["amount"]        # Total
            ]

            # Group the stocks into dictionary for further processing.
            if order_entry_instrument["symbol"] not in stocks_dict:
                stocks_dict[order_entry_instrument["symbol"]] = [stock_entry]
            else:
                stocks_dict[order_entry_instrument["symbol"]].append(stock_entry)

        # Assemble options data tablerows
        options_tablerows = []
        for symbol in stocks_dict:
            # Sort the stocks for each symbol by date (column 2).
            stocks = sorted(stocks_dict[symbol], key=lambda x: x[2])
            options_tablerows += stocks

        save_dataset_to_file(
            "stockdata",
            fileformat,
            "Transactions",
            ['Ticker', 'Name', 'Date', 'Quantity', 'Price', 'TranType', 'Fees', 'Total'],
            options_tablerows
        )

def get_api_token():
    """Returns the user's Robinhood API token stored in token.txt.

    Returns:
        string: API bearer token.
    """
    with open("token.txt") as token_file:
        content = token_file.readlines()
    content = [x.strip() for x in content]
    return content[0]

def save_to_json_file(file_contents, filename):
    """Store the contents of a variable in a json file in the results/ folder.

    Args:
        file_contents (any): List or Dictionary to dump into the file.
        filename (string): Filename.
    """
    with open(f"results/{filename}.json", 'w') as outfile:
        json.dump(file_contents, outfile)

def save_dataset_to_file(filename, fileformat, title, headers, data):
    """Store a given dataset as the requested file format.

    Args:
        filename (string): Filename.
        fileformat (string): Requested file format to export, default .xls.
        title (string): Title
        headers (list): String list of table headers.
        rows (list): Two-dimensional list of table rows.
    """
    dataset = tablib.Dataset(*data, title=title, headers=headers)
    if fileformat == "html":
        with open(f"results/{filename}.html", "w") as html_file:
            html_file.write(dataset.export('html'))
    else:
        with open(f"results/{filename}.xls", "wb") as xls_file:
            xls_file.write(dataset.export('xls'))
