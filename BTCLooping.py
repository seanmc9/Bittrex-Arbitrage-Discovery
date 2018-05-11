'''
Created on Nov 24, 2017

@author: sean1000444
'''

import json
import requests
import hmac
import hashlib
import time

GET_BALANCE = "getbalance?"             #currency
GET_ORDER_HISTORY = "getorderhistory?"  #nothing

BUY_LIMITORDER = "buylimit?"            #pair, quant, and price
SELL_LIMITORDER = "selllimit?"          #same
CANCEL_ORDER = "cancel?"                #uuid
GET_OPENORDERS = "getopenorders?"       #pair

api_secret = ""
nonce = str(int(time.time() * 1000))
api_key = ""

def trade_request (type_of_request, params = []):
    request_url = "https://bittrex.com/api/v1.1/market/" + type_of_request
    request_url = "{0}apikey={1}&nonce={2}&".format(request_url, api_key, nonce)

    if(type_of_request == BUY_LIMITORDER or type_of_request == SELL_LIMITORDER) :
        request_url += "&market=" + params.pop(0)
        request_url += "&quantity=" + params.pop(0)
        request_url += "&rate=" + params.pop(0)
    elif(type_of_request == CANCEL_ORDER) :
        request_url += "&uuid=" + params.pop()
    elif(type_of_request == GET_OPENORDERS) :
        request_url += "&market=" + params.pop()
    elif(type_of_request == GET_BALANCE) :
        request_url = "https://bittrex.com/api/v1.1/account/" + type_of_request
        request_url = "{0}apikey={1}&nonce={2}&".format(request_url, api_key, nonce)
        request_url += "&currency=" + params.pop()
    else :
        request_url = "https://bittrex.com/api/v1.1/account/" + type_of_request
        request_url = "{0}apikey={1}&nonce={2}&".format(request_url, api_key, nonce)
        

    apisign = hmac.new(api_secret.encode(), request_url.encode(), hashlib.sha512).hexdigest()

    r = requests.get(
            request_url,
            headers={"apisign": apisign},
            timeout=10
        ).json()

    print(r)
    return r

def parse_markets (url):
    r = requests.get(url)
    text = r.text
    parsed = json.loads(text)
    totalMarkets = parsed.get("result")
    return totalMarkets

url_foundation = "https://bittrex.com/api/v1.1/public/getticker?market="

currLists = ["ETH-MANA", "ETH-CVC", "ETH-BAT", "ETH-TKN", "ETH-FUN", "ETH-GNO", "ETH-REP", "ETH-ANT"]

#Constantly loops through this list, if it comes across an arb opportunity, it will execute it
#BEWARE: Does not check to see if prev orders completed or even were sent successfully yet
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
            result = 1000.0 * fee * (1.0/BAlt_Ask) * fee * EAlt_Bid * fee * BE_Bid
            resultO = 1000.0 * fee * (1.0/BE_Ask) * fee * (1.0/EAlt_Ask) * fee * BAlt_Bid

            min_trade_quant = 0.001

            if((result > initial) & (result > resultO)):
                print(current_pair)
                print("Forwards BTC/ALT/ETH/BTC:", ((result-initial)/initial)*100, "%")
                print("F:", result, "B:", resultO)
                btc_to_alt = trade_request(BUY_LIMITORDER, ["BTC"+current_pair[3:], str(min_trade_quant*(BAlt_Ask)), str(BAlt_Ask)])
                time.sleep(3) #This is how long it takes for the requests to go through anyways
                #We only do this check on the first one because if the second doesn't go through we will just have to continue
                #when I make an overarching program of this to manage funds and risk it will be updated
                if(trade_request(GET_OPENORDERS, ["BTC"+current_pair[3:]])) : trade_request(CANCEL_ORDER, [btc_to_alt.get("result").get("uuid")])
                alt_to_eth = trade_request(SELL_LIMITORDER, ["ETH"+current_pair[3:], str(min_trade_quant*(EAlt_Bid)), str(EAlt_Bid)])
                eth_to_btc = trade_request(SELL_LIMITORDER, ["BTC-ETH", str(min_trade_quant*(1/BE_Bid)), str(BE_Bid)])
                print("You have successfully completed an arbitrage trade changing", min_trade_quant, "BTC to", trade_request(GET_ORDER_HISTORY).get("result").pop(0).get("Quantity"), "BTC")
                
            elif ((resultO > initial) & (resultO > result)):
                print(current_pair)
                print("Backwards BTC/ETH/ALT/BTC with", ((resultO-initial)/initial)*100, "%")
                print("F:", result, "B:", resultO)
                btc_to_eth = trade_request(BUY_LIMITORDER, ["BTC-ETH", str(min_trade_quant*BE_Ask), str(BE_Ask)])
                time.sleep(3)
                if(trade_request(GET_OPENORDERS, ["BTC-ETH"])) : trade_request(CANCEL_ORDER, [btc_to_eth.get("result").get("uuid")])
                eth_to_alt = trade_request(SELL_LIMITORDER, ["ETH"+current_pair[3:], str(min_trade_quant*(EAlt_Ask)), str(EAlt_Ask)])                    
                alt_to_btc = trade_request(SELL_LIMITORDER, ["BTC"+current_pair[3:], str(min_trade_quant*(BAlt_Bid)), str(BAlt_Bid)])
                print("You have successfully completed an arbitrage trade changing", min_trade_quant, "BTC to", trade_request(GET_ORDER_HISTORY).get("result").pop(0).get("Quantity"), "BTC")
                
            else:
                print(item, "F:", str(result), "B:", str(resultO))
                continue
