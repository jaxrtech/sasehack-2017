import logging
from pprint import pprint
from flask import Flask
from flask import request, jsonify

logging.basicConfig(level=logging.DEBUG)
app = Flask(__name__)


@app.route('/webhook', methods=['POST'])
def webhook():
    json = request.get_json()
    pprint(json)

    intent = json['result']['metadata']['intentName']
    print("INTENT='{}'".format(intent))

    text = "THE WEBHOOK WORKS THIS TIME!!!"
    result = {
        'speech': text,
        'displayText': text
    }

    pprint(result)
    return jsonify(result)


@app.route('/')
def hello_world():
    return 'Hello World!!'


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080)

