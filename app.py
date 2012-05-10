import os
import logging
import json

import flask
from flask import Flask
from flask import Markup
from flask import request
from flask import make_response, render_template

import bs4
from bs4 import BeautifulSoup

import re

import requests

app = Flask(__name__)

# debug
dbg = app.logger.debug

def scrape(url):
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

@app.route('/')
def main():
    url = request.args.get('url', '')
    if url:
		return scrape(url)
    else:
        return '<pre>Woah there, we need a URL.\nExample: ' + request.url_root + '?url=http://www.google.com </pre>'

@app.route('/debug')
def debug():
    url = request.args.get('url', '')
    


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
