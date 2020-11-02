#!/usr/bin/env python
"""Script that exports Robinhood watchlist, options, and orders data."""

from rh_data_collector import RHDataCollector

if __name__ == "__main__":
    robinhood = RHDataCollector()

while True:
    input_val = input("\n\n 1. Export watchlist.\n 2. Export stock transactions. \n 3. Export option transactions. \n 4. Exit. \n\n Please enter your input (1, 2, 3 or 4) : ")

    if input_val == "1":
        print("\n\nExporting watchlist...")
        robinhood.export_watchlist_data()
        print("\nCompleted. Check the results folder.\n")
        break
    elif input_val == "2":
        print("\n\nExporting stock transactions...")
        robinhood.export_stock_data()
        print("\nCompleted. Check the results folder.\n")
        break
    elif input_val == "3":
        print("\n\nExporting option transactions...")
        robinhood.export_options_data()
        print("\nCompleted. Check the results folder.\n")
        break
    elif input_val == "4":
        print("\n\nExiting...\n")
        break
    else:
        print("\n\nPlease enter a valid input.\n")
