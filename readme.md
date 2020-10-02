# MyRobinhoodData

A wrapper around Robinhood API calls to export your watchlist, options history, and stocks order history to JSON, HTML, or XLS files.

## Getting Started

### Setting up the project

Download the repo/code to a folder on your laptop via the green code button. Install the dependencies listed in `requirements.txt.`

```sh
pip install -r requirements.txt
```

You'll also need to install the `tablib` export filetype add-on dependencies separately, depending on which one you want to use:

```sh
pip install 'tablib[html]'
pip install 'tablib[xls]'
```

### Obtaining and saving your Robinhood API token

1. Login to Robinhood on your browser.
2. Right click the page and click "Inspect". This will open up your developer console.
3. Now in the developer console, open the Network tab and search for "orders".
4. Select the first option and scroll down until you see a section titled "Request Headers".

![Walkthrough for getting Robinhood API token via Google Chrome's Network Tab](tokenWalkthrough.png)
_You'll need the full text of that authorization sectiion. It's blacked out here for privacy._

5. Copy everything that appears after "Bearer" to your clipboard. This is your API bearer token.
6. Paste the token into `token.example.txt`. Rename the file to `token.txt`. `.gitignore` has this file ignored for your privacy to prevent it from being committed to the repo.

Alternatively, instead of saving your token to `token.txt`, you can pass in this string when initializing the RobinhoodAPIWrapper class:

```py
from robinhood_api_wrapper import RobinhoodAPIWrapper

if __name__ == "__main__":
    robinhood = RobinhoodAPIWrapper("YOUR_TOKEN_HERE")
```

## Running the project

`robinhood_api_wrapper.py` is set up to export your watchlist, options history, and stocks order history to HTML or XLS files. `src/main.py` is all set up for you to export all three to HTML as-is. Whether you're exporting as HTML or XLS, JSON files for the paginated API collection data will also be generated.

```py
robinhood = RobinhoodAPIWrapper()

robinhood.export_watchlist_data("html")
robinhood.export_options_data("html")
robinhood.export_orders_data("html")
```

```sh
python src/main.py
```

If you want to export xls instead:

```py
robinhood = RobinhoodAPIWrapper()

robinhood.export_watchlist_data("xls")
# xls is the default file format, so this will work too:
robinhood.export_options_data()
```
