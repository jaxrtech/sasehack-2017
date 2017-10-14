import logging
from pprint import pprint

from flask import Flask
from flask import request
from flask_marshmallow import Marshmallow
from marshmallow import fields, pprint

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
ma = Marshmallow(app)


class FollowupEventSchema(ma.Schema):
    name = fields.Str()
    data = fields.Dict()


class FollowupEvent:
    def __init__(self, name, data=None):
        self.name = name
        self.data = data or {}


class ResponseSchema(ma.Schema):
    speech = fields.Str()
    display_text = fields.Str(attribute='displayText')
    followup_event = fields.Nested(FollowupEventSchema)


class Response:
    def __init__(self, text, followup_event=None):
        self.speech = text
        self.display_text = text
        self.followup_event = followup_event


@app.route('/webhook', methods=['POST'])
def webhook():
    json = request.get_json()
    pprint(json)

    intent = json['result']['metadata']['intentName']
    print("INTENT='{}'".format(intent))

    text = "THE WEBHOOK WORKS THIS TIME!!!"
    result = Response(text, FollowupEvent('initial_question'))
    pprint(result)

    # {
    #     'speech': text,
    #     'displayText': text,
    #     'followupEvent': {
    #         'name': 'initial_question',
    #         "data": {}
    #     }
    # }

    return ResponseSchema().jsonify(result)


@app.route('/')
def hello_world():
    return 'Hello World!!'


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080)

