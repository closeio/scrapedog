import os
import logging
import json

from scraper import ScrapeDog

from flask import Flask, Markup, request, jsonify, make_response, render_template

app = Flask(__name__)

# debug
dbg = app.logger.debug



def scrape(url, callback=None):
    scraper = ScrapeDog(url=url)
    response = scraper.get_content()

    if callback:
        return '%s(%s)' % (callback, json.dumps(response))
    else:
        return jsonify(response)


@app.route('/')
def main():
    url = request.args.get('url', '')
    if url:
	return scrape(url, request.args.get('callback', ''))
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

