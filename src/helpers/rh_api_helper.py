#!/usr/bin/env python
"""Class to interact with the Robinhood API and export data."""

import json
import requests
import tablib
from pathlib import Path

class RHApiHelper:
    """Class to make the calls to Robinhood API's and save data as JSON/Excel.
    """

    def __init__(self, auth_token = None):
        self.base_path = Path(__file__).parent
        self.auth_token = auth_token or self.get_api_token()

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
            "x-robinhood-api-version": "1.411.9"
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

    def get_api_token(self):
        """Returns the user's Robinhood API token stored in token.txt.

        Returns:
            string: API bearer token.
        """
        
        file_path = (self.base_path / "../../token.txt").resolve()
        with open(file_path) as token_file:
            content = token_file.readlines()
        content = [x.strip() for x in content]
        return content[0]

    def save_to_json_file(self, file_contents, filename):
        """Store the contents of a variable in a json file in the results/ folder.

        Args:
            file_contents (any): List or Dictionary to dump into the file.
            filename (string): Filename.
        """
        file_path = (self.base_path / f"../../results/{filename}.json").resolve()
        with open(file_path, 'w') as outfile:
            json.dump(file_contents, outfile)

    def save_dataset_to_excel(self, filename, fileformat, dataset):
        """Store a given dataset as the requested file format.

        Args:
            filename (string): Filename.
            fileformat (string): Requested file format to export, default .xls.
            dataset (tablib dataset): data containing the data to be written to excel file
        """
        file_path = (self.base_path / f"../../results/{filename}.xls").resolve()
        with open(file_path, "wb") as xls_file:
            xls_file.write(dataset.export('xls'))
    
    def save_dataset_to_file(self, filename, fileformat, title, headers, data):
        """Store a given dataset as the requested file format.
        Args:
            filename (string): Filename.
            fileformat (string): Requested file format to export, default .xls.
            title (string): Title
            headers (list): String list of table headers.
            rows (list): Two-dimensional list of table rows.
        """
        file_path = (self.base_path / f"../../results/{filename}.{fileformat}").resolve()
        dataset = tablib.Dataset(*data, title=title, headers=headers)
        if fileformat == "html":
            with open(file_path, "w") as html_file:
                html_file.write(dataset.export('html'))
        else:
            with open(file_path, "wb") as xls_file:
                xls_file.write(dataset.export('xls'))