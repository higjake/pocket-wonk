#!/usr/bin/env python
from __future__ import print_function
from future.standard_library import install_aliases
install_aliases()
from urllib.parse import urlparse, urlencode
from urllib.request import urlopen, Request
from urllib.error import HTTPError
import json
import os
import time
from flask import Flask
from flask import request
from flask import make_response

categoryMap = {
    'POP': {
        'definition': 'population'
    }
}

# Flask app should start in global layout
app = Flask(__name__)
@app.route('/webhook', methods=['POST'])
def webhook():
    start = time.time()
    req = request.get_json(silent=True, force=True)
    print("Request:")
    print(json.dumps(req, indent=4))
    res = processRequest(req)
    res = json.dumps(res, indent=4)
    # print(res)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    end = time.time()
    print('Duration: {:10.4f} seconds'.format(end - start))
    return r
def processRequest(req):
    baseurl = "https://api.census.gov/data/"
    url_query = makeQuery(req)
    if url_query is None:
        return {}
    final_url = baseurl + url_query
#     #final_url = baseurl + urlencode({url_query})
#     #final_url = "https://www.expertise.com/api/v1.0/directories/ga/atlanta/flooring"
    result = urlopen(final_url).read()
    data = json.loads(result)
    res = makeWebhookResult(data)
    return res
def makeQuery(req):
    result = req.get("result")
    contexts = result.get("contexts")
    parameters = contexts[0].get("parameters")
    state = parameters.get("state")
    target_metric = parameters.get("target-metric")
    year = parameters.get("year")
    if parameters.get("year") is None:
        return "2014"
    
    return year + "/pep/natstprc?get=STNAME," + target_metric + "&DATE=1&for=state:" + state

def makeWebhookResult(data):
    array1 = data[1]
    if array1 is None:
        return {
        "speech": "this failed",
        "displayText": "this failed",
        # "data": data,
        # "contextOut": [],
        "source": "apiai-weather-webhook-sample"}
    
    # print(json.dumps(item, indent=4))
    array1 = data[1] # Adding this line as a sanity check
    categories = data[0]
    lookup_value = categories[1]
    speech = "The " + categoryMap[lookup_value]['definition'] + " for " + array1[0] + " is " + array1[1] + ". What else can I help you with?"
#     actionMap[action]['speech'] % tuple([providers[i].get(actionMap[action]['key']) for i in range(actionMap[action]['count'])]);
#     speech = "The top three providers in your area are " + providers[0].get('business_name') + ", " + providers[1].get('business_name') + ", and " + providers[2].get('business_name') + "." 
    print("Response:")
    print(speech)
    return {
        "speech": speech,
        "displayText": speech,
        # "data": data,
        # "contextOut": [],
        "source": "apiai-weather-webhook-sample"
    }
if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    print("Starting app on port %d" % port)
    app.run(debug=False, port=port, host='0.0.0.0')
