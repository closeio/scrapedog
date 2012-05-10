import os
import logging
import json
import re
import requests

from flask import Flask, Markup, request, jsonify, make_response, render_template

from bs4 import BeautifulSoup

soup = None
app = Flask(__name__)

# debug
dbg = app.logger.debug

def scrape(url):
    r = requests.get(url)
    global soup
    soup = BeautifulSoup(r.text)

    meta_tags = []
    meta_tags_soup= soup.head.find_all('meta')
    for meta in meta_tags_soup:
        meta_tags.append(meta.attrs)

    response = {
        'url': url,
        'title': soup.title.string,
        'headers': r.headers,
        'meta_tags': meta_tags
    }

    return response

@app.route('/')
def main():
    url = request.args.get('url', '')
    if url:
        if bool(re.match('.*scrapedog.herokuapp.*',url)):
            return '&#x0CA0;_&#x0CA0;'
        else:
            callback = request.args.get('callback', '')
            response = scrape(url)

            if callback:
                return '%s(%s)' % (callback, json.dumps(response))
            else:
                return jsonify(response)

    else:
        return '<pre>Woah there, we need a URL.\nExample: ' + request.url_root + '?url=http://www.google.com </pre>'

@app.route('/debug')
def debug():
    global soup

    url = request.args.get('url', '')

    output = scrape(url)
    nodes_numbers = soup.find_all(text=re.compile('(\d{3}\D{1,7}){2}\d{3}'))

    return jsonify(output)


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
