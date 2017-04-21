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
    'B01001_002E': {
        'definition': 'According to the 2015 American Community Summary, the male population of ',
        'definition2': ' is ',
        'definition3': '.',
        'pretext1': 'The male population of ',
        'pretext2': ' is ',
        'pretext3': '. This is ',
        'pretext4': '% of the total population.',
        'slack-url': 'https://www.census.gov/programs-surveys/acs/data/summary-file.html',
        'slack-title': 'Find out more from the American Census Summary (2015)'
    },
    'POP': {
        'definition': 'The population for ',
        'definition2': ' is ',
        'definition3': '. What else can I help you with?'
    },
    'POV': {
        'definition': 'The poverty rate at last census (2015) was ',
        'definition2': ' percent, with ',
        'definition3': '000 individuals living in poverty nationwide. What else can I help you with?'
    },
    'RCPTOT': {
        'definition': 'At last census (2012), the number of employees was ',
        'definition2': '. The industry generated $',
        'definition3': '000 annually. What else can I help you with? You can look up industry employment figures and valuations by city, state, county, or nationwide. '
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
    action = result.get("action")
    contexts = result.get("contexts")
    parameters = contexts[0].get("parameters")
    target_metric = parameters.get("target-metric")
    year = parameters.get("year")
    race = parameters.get("race")
    metro_area = parameters.get("metro-area")
    naics_code = parameters.get("industry")
    countycitystate = parameters.get("county-state")
    splitCCS = countycitystate.split( )
    state = splitCCS[1] #state can be actual state or metro area/city
    print(state)
    county = splitCCS[0]
    print(county)
    if target_metric == "timeseries/poverty/histpov2?get=PCTPOV,POV,POP&time=":
        return target_metric + year + "&RACE=" + race
    elif action == "industryEmploymentRequest":
        if county == "*":
            if state == "*":
                return target_metric + "&for=us:*&NAICS2012=" + naics_code
            return target_metric + "&for=state:" + state + "&NAICS2012=" + naics_code
        elif county == "city":
            return target_metric + "&for=metropolitan+statistical+area/micropolitan+statistical+area:" + state + "&NAICS2012=" + naics_code
        return target_metric + "&for=county:" + county + "&in=state:" + state + "&NAICS2012=" + naics_code
    elif action == "getPopulation":
        if county == "*":
            if state == "*":
                return year + target_metric + "&for=us:*"
            return year + target_metric + "&for=state:" + state
        elif county == "city":
            return year + target_metric + "&for=metropolitan+statistical+area/micropolitan+statistical+area:" + state
        return year + target_metric + "&for=county:" + county + "&in=state:" + state
    elif action == "demographicRequest":
        if county == "*":
            if state == "*":
                return target_metric + ",B01001_001E&for=us:*"
            return target_metric + ",B01001_001E&for=state:" + state
        elif county == "city":
            return target_metric + ",B01001_001E&for=metropolitan+statistical+area/micropolitan+statistical+area:" + state
        return target_metric + ",B01001_001E&for=county:" + county + "&in=state:" + state

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
    speech = categoryMap[lookup_value]['definition'] + array1[0] + categoryMap[lookup_value]['definition2'] + array1[1] + categoryMap[lookup_value]['definition3']
    print("Response:")
    print(speech)
    slack_text = categoryMap[lookup_value]['pretext1'] + array1[0] + categoryMap[lookup_value]['pretext2'] + array1[1] + categoryMap[lookup_value]['pretext3'] + array1[1]/array1[2]*100 + categoryMap[lookup_value]['pretext4'] 
    slack_message = {
        "text": speech,
    }
    print(slack_message)
    return {
        "speech": speech,
        "displayText": speech,
        "data": {
            "slack": slack_message
        },
        # "contextOut": [],
        "source": "apiai-weather-webhook-sample"
    }
if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    print("Starting app on port %d" % port)
    app.run(debug=False, port=port, host='0.0.0.0')
