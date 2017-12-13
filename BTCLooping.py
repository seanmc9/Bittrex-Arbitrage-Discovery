'''
Created on Nov 24, 2017

@author: sean1000444
'''

import json
import requests

def parse_markets (url):
    r = requests.get(url)
    text = r.text
    parsed = json.loads(text)
    totalMarkets = parsed.get("result")
    return totalMarkets

# totalMarkets = parse_markets("https://bittrex.com/api/v1.1/public/getmarketsummaries")
url_foundation = "https://bittrex.com/api/v1.1/public/getticker?market="

currLists = ["ETH-MANA", "ETH-CVC", "ETH-BAT", "ETH-TKN", "ETH-FUN", "ETH-GNO", "ETH-REP", "ETH-ANT"]       #The order of the totalMarkets in totalMarkets changes, so I just have to define the appendages myself unless I want to do all totalMarkets

while(True):

    urlBE = url_foundation + "BTC-ETH"

    while(True):

        for item in currLists:

            d = parse_markets(urlBE)
            try:
                BE_Ask = d.get("Ask")
                BE_Bid = d.get("Bid")
            except AttributeError:
                break

            current_pair = item

            url_ETH = url_foundation + str(current_pair)
            d = parse_markets(url_ETH)
            try:
                EAlt_Ask = d.get("Ask")
                EAlt_Bid = d.get("Bid")
            except AttributeError:
                continue

            url_BTC = url_foundation + "BTC" + str(current_pair[3:])
            d = parse_markets(url_BTC)
            try:
                BAlt_Ask = d.get("Ask")
                BAlt_Bid = d.get("Bid")
            except AttributeError:
                continue

            initial = 1000.0
            fee = 0.9975
            result = 1000.0 * fee * (1/BAlt_Ask) * fee * EAlt_Bid * fee * BE_Bid
            resultO = 1000.0 * fee * (1.0/BE_Ask) * fee * (1.0/EAlt_Ask) * fee * BAlt_Bid

            if((result > initial) & (result > resultO)):
                print(current_pair)
                print("Forwards BTC/ALT/ETH/BTC:", ((result-initial)/initial)*100, "%")
                print("F:", result, "B:", resultO)
    #             r = requests.get("https://bittrex.com/api/v1.1/market/buylimit?apikey=API_KEY&market=BTC-LTC&quantity=1.2&rate=1.3")

            elif ((resultO > initial) & (resultO > result)):
                print(current_pair)
                print("Backwards BTC/ETH/ALT/BTC with", ((resultO-initial)/initial)*100, "%")
                print("F:", result, "B:", resultO)
            else:
                # print(item, "F:", str(result), "B:", str(resultO))
                continue
