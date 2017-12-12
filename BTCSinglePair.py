'''
@author: sean1000444
'''
import requests
import json
import time

alt = "MANA"

while (True):

    while (True):
        url1 = "https://bittrex.com/api/v1.1/public/getticker?market=BTC-" + str(alt)
        r = requests.get(url1)
        text = r.text
        parsed = json.loads(text)
        d = parsed.get("result")
        BN_Ask = d.get("Ask")
        BN_Bid = d.get("Bid")

        url2 = "https://bittrex.com/api/v1.1/public/getticker?market=ETH-" + str(alt)
        r = requests.get(url2)
        text = r.text
        parsed = json.loads(text)
        d = parsed.get("result")
        EN_Ask = d.get("Ask")
        EN_Bid = d.get("Bid")

        url3 = "https://bittrex.com/api/v1.1/public/getticker?market=BTC-ETH"
        r = requests.get(url3)
        text = r.text
        parsed = json.loads(text)
        d = parsed.get("result")
        BE_Ask = d.get("Ask")
        BE_Bid = d.get("Bid")

        initial = 1000.0
        fee = 0.9975
        result = 1000.0 * fee * (1/BN_Ask) * fee * EN_Bid * fee * BE_Bid
        resultO = 1000.0 * fee * (1.0/BE_Ask) * fee * (1.0/EN_Ask) * fee * BN_Bid

        if((result > initial) & (result > resultO)):
            print("Forwards BTC/ALT/ETH/BTC:", ((result-initial)/initial)*100, "%")
            print("F:", result, "B:", resultO)
        elif ((resultO > initial) & (resultO > result)):
            print("Backwards BTC/ETH/ALT/BTC:", ((resultO-initial)/initial)*100, "%")
            print("F:", result, "B:", resultO)
        else:
            print("Both returned under initial.")
            print("F:", result, "B:", resultO)
        time.sleep(5)
