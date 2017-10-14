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
        self.data = data


class Response:
    def __init__(self, text=None, followup_event=None):
        self.speech = text
        self.display_text = text
        self.followup_event = followup_event


class ResponseSchema(ma.Schema):
    speech = fields.Str()
    displayText = fields.Str(attribute='display_text')
    followupEvent = fields.Nested(FollowupEventSchema, attribute='followup_event')


class UserInput:
    def __init__(self, text: str, action: str, intent: str):
        self.raw = text
        self.action = action
        self.intent = intent


def respond_to(input: UserInput) -> Response:
    if input.action == 'foobar':
        return Response()

    if input.action == 'input.unknown':
        if not input.raw.startswith('/'):
            return Response()

        xs = input.raw.split(' ')
        verb = xs[0].lstrip('/')
        args = xs[1:]
        print("verb={0!r}, args={1!r}".format(verb, args))

        if verb == 'question':
            if len(args) != 1:
                return Response()

            code = args[0]
            return Response(followup_event=FollowupEvent('question-{}'.format(code)))

        return Response()

    if input.intent == 'start':
        return Response(followup_event=FollowupEvent('initial_question'))


@app.route('/webhook', methods=['POST'])
def webhook():
    print(ResponseSchema().dump(Response(followup_event=FollowupEvent('question-{}'.format('a2')))).data)

    json = request.get_json()
    pprint(json)

    raw = json['result']['resolvedQuery']
    action = json['result']['action']
    intent = json['result']['metadata']['intentName']
    print("ACTION='{}', INTENT='{}'".format(action, intent))

    text = "THE WEBHOOK WORKS THIS TIME!!!"
    result = respond_to(UserInput(raw, action, intent))
    print(ResponseSchema().dump(result).data)

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

