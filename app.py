import os
import logging
import json

import flask
from flask import Flask
from flask import Markup
from flask import request

import bs4
from bs4 import BeautifulSoup

import requests

app = Flask(__name__)

# debug
dbg = app.logger.debug

@app.route('/')
def main():
    url = request.args.get('url', '')
    if url:
        # callback for jsonp
        callback = request.args.get('callback', '')
        
        r = requests.get(url)
        html = BeautifulSoup(r.text)
        
        meta_tags = []
        meta_tags_bs = html.find_all('meta')
        for meta in meta_tags_bs:
            meta_tags.append(meta.attrs)
        
        response = {
            'url': url,
            'title': html.title.string,
            'headers': r.headers,
            'meta_tags': meta_tags
        }
        
        if callback:
            return '%s(%s)' % (callback, json.dumps(response)) 
        else:
            return json.dumps(response)
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
    app.run(host='0.0.0.0',
            port=port,
            debug=True)
