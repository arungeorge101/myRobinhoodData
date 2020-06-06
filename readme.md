Instructions

1. Download the above repo/code to a folder in your laptop
2. Login to Robinhood on your browser
3. Right click the page and click "Inspect". This will open up your developer console.
4. Now in the developer console, open the Network tab and find the call /orders (https://api.robinhood.com/orders/)
5. Right click this copy -> copy as curl. Paste this on to notepad. This should look something like this: 

curl 'https://api.robinhood.com/orders/' -H 'authority: api.robinhood.com' -H 'x-robinhood-api-version: 1.315.0' -H 'sec-fetch-dest: empty' -H 'authorization: Bearer {***} -H 'user-agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36' -H 'dnt: 1' -H 'accept: */*' -H 'origin: https://robinhood.com' -H 'sec-fetch-site: same-site' -H 'sec-fetch-mode: cors' -H 'referer: https://robinhood.com/' -H 'accept-language: en-US,en;q=0.9' --compressed

6. Copy your personal authorization token, Everything after Bearer in "authorization: Bearer {***}"
7. Open the file rhDataAnalyzer.py. Paste the authorization token to line 28 between the quotes
8. Now open terminal and browse to the same folder and run pip install -r requirements.txt - this is to install all the dependencies for the application.
9. Then run  python ./rhDataAnalyzer.py from your terminal
10. This will first call robinhood and create orders.json file with all your stock information.
11. Next if you have options data it will create options.json
12. This will create an excel file stockdata.xls in the same folder with all the transactions data (Name, Ticker, Date, Price, Quantity, Totalprice , TranType, Fees) 
13. This will create an excel file optionsdata.xls in the same folder with all the transactions data (Ticker, Date, Price, Quantity, Totalprice , TranType,) 
14. Summary sheet for stock and options data - IN PROGRESS