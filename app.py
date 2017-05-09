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

videoArray = ['https://www.youtube.com/watch?v=9ogQ0uge06o','https://www.youtube.com/watch?v=V-zXT5bIBM0','https://www.youtube.com/watch?v=nXpB1rixnPQ','https://www.youtube.com/watch?v=Pa0lMzaljTk','https://www.youtube.com/watch?v=nbY_aP-alkw','https://www.youtube.com/watch?v=nPImqZo0D74']

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
    if req.get('result').get('action') != 'randomdisney':
        return {}
    import random
    random_number = random.randint(0,5)
    print(random_number)
    speech = videoArray[random_number]
    print("Response:")
    print(speech)
    slack_text = "<" + speech + ">"
    print("Slack Response:")
    print(slack_text)
    slack_message = {
        "text": slack_text,
    }
    return {
        "speech": speech,
        "displayText": speech,
        "data": {
            "slack": slack_message
        },
        # "contextOut": [],
        "source": "Jake Higdon"
    }

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    print("Starting app on port %d" % port)
    app.run(debug=False, port=port, host='0.0.0.0')
