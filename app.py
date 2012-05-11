import re
import os
import logging
import json
import re

from scraper import ScrapeDog

from flask import Flask, Markup, request, jsonify, make_response, render_template

soup = None
app = Flask(__name__)

# debug
dbg = app.logger.debug


def scrape(url):
    scraper = ScrapeDog(url=url)
    response = scraper.get_content()

    global soup
    soup = scraper.soup

    return response


@app.route('/')
def main():
    url = request.args.get('url', '')
    if url:
        if bool(re.match(request.host, url)):
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
    app.run(host='127.0.0.1',
            port=port,
            debug=True)

