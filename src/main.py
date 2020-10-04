#!/usr/bin/env python
"""Script that exports Robinhood watchlist, options, and orders data."""

from robinhood_api_wrapper import RobinhoodAPIWrapper

if __name__ == "__main__":
    robinhood = RobinhoodAPIWrapper()

    robinhood.export_watchlist_data()
    robinhood.export_options_data()
    robinhood.export_orders_data()
