import os
import logging
import json

import flask
from flask import Flask
from flask import Markup
from flask import request

import requests

app = Flask(__name__)

@app.route('/')
def main():
    url = request.args.get('url', '')
    if url:
        r = requests.get(url)
        return 'abc' 
    else:
        return 'Hello World!'

@app.route('/dummy')
def dummy():
    obj = {'url': 'http://www.google.com/',
           'title': 'Google',
           'http_headers': {'Content-Type': 'text/html',
                            'Status': 200 
                            },
           'meta_tags': {'description': 'The homepage of the internet.'}
    }
    return json.dumps(obj)

if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
