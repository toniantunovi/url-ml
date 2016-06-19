"""RESTful inteface for getting UrlRNN predictions."""
import os
import json
from flask import Flask
from flask.ext.cors import CORS
from flask import request
from urlparse import urlparse
from prediction.prediction import predict

APP = Flask(__name__)
APP.debug = True
CORS(APP)

@APP.route('/urlml', methods=['POST'])
def get_predictions():
    """Get urls from request and return UrlRnn output."""
    if not request.json or not 'urls' in request.json:
        return {'Error': 'Request data need to have JSON array with urls in format: '
                         ' { "urls": ["url1", "url2"] }'}

    urls = request.json['urls']

    # Example return string:
    # {"urls": [{"reputation":[{"domain": "facebook.com", "malicious": 0.32, "non-malicious": 99.68},
    # {"url": "http://facebook.com/anything.exe", "malicious": 94.26, "non-malicious": 5.74}]}]}
    predictions = '{"urls": ['
    for url in urls:
        url = url.lower()

        if "//" not in url[0:8]:
            url = "//" + url

        url_parsed = urlparse(url)
        domain = url_parsed.netloc

        url = url[url.find("//")+2:]

        predictions += '{"reputation":['

        [dp_1, dp_2] = predict([domain])
        dp_1 = round(dp_1*100, 2)
        dp_2 = round(dp_2*100, 2)
        predictions += json.dumps({'domain': domain, 'non-malicious': dp_1, 'malicious': dp_2})

        predictions += ", "

        [p_1, p_2] = predict([url])
        p_1 = round(p_1*100, 2)
        p_2 = round(p_2*100, 2)
        predictions += json.dumps({'url': url, 'non-malicious': p_1, 'malicious': p_2})
        predictions += "]}, "

    predictions = predictions[:len(predictions)-2]
    predictions += "]}"
    return predictions

if __name__ == '__main__':
    HOST = os.environ.get('SERVER_HOST', '0.0.0.0')
    try:
        PORT = int(os.environ.get('SERVER_PORT', '5555'))
    except ValueError:
        PORT = 5555
    APP.run(HOST, PORT)
