import logging
from pprint import pprint

import sqlalchemy as sa
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import select
from sqlalchemy.dialects import postgresql
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker, relationship
from marshmallow_sqlalchemy import ModelSchema

from flask import Flask, jsonify
from flask import request
from flask_marshmallow import Marshmallow
from marshmallow import fields, pprint

from sasehack import settings
from sasehack.models import UserInput, Response, FollowupEvent

logging.basicConfig(level=logging.DEBUG)


def make_connection_str(user, password, db, host='localhost', port=5432):
    # We connect with the help of the PostgreSQL URL
    # postgresql://federer:grandestslam@localhost:5432/tennis
    url = 'postgresql://{}:{}@{}:{}/{}'
    url = url.format(user, password, host, port, db)
    return url


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = make_connection_str(
    user=settings.POSTGRES_USER,
    password=settings.POSTGRES_PASSWORD,
    db=settings.POSTGRES_DATABASE,
    host=settings.POSTGRES_HOST,
    port=settings.POSTGRES_PORT
)

db = SQLAlchemy(app)
ma = Marshmallow(app)


### DB SCHEMA ###

class Answer(db.Model):
    __tablename__ = 'answer'
    id = db.Column(db.Integer, primary_key=True)

    property_id = db.Column(db.Integer, db.ForeignKey('property.id'))
    property = db.relationship('Property', backref='answer')

    question_id = db.Column(db.Integer, db.ForeignKey('question.id'))
    question = db.relationship('Question', backref='answer')

    def __repr__(self):
        return '<Answer(id={self.id!r}, property_id={self.property_id!r}, question_id={self.question_id!r})>'.format(self=self)


class Property(db.Model):
    __tablename__ = 'property'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)

    property_type_id = db.Column(db.Integer, db.ForeignKey('property_type.id'))
    property_type = db.relationship('PropertyType', backref='property')

    def __repr__(self):
        return '<Property(name={self.name!r})>'.format(self=self)

class PropertyType(db.Model):
    __tablename__ = 'property_type'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    intent = db.Column(db.String)

class Question(db.Model):
    __tablename__ = 'question'
    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.String)

    property_id = db.Column(db.Integer, db.ForeignKey('property.id'))
    property = db.relationship('Property', backref='question')


### MODEL SCHEMA ###

class AnswerSchema(ma.ModelSchema):
    class Meta:
        model = Answer

answer_schema = AnswerSchema()


class PropertySchema(ma.ModelSchema):
    class Meta:
        model = Property

property_schema = PropertySchema()


class PropertyTypeSchema(ma.ModelSchema):
    class Meta:
        model = PropertyType

property_type_schema = PropertyTypeSchema()


class QuestionSchema(ma.ModelSchema):
    class Meta:
        model = Question

questions_schema = QuestionSchema()


### APPLICATION ###

class FollowupEventSchema(ma.Schema):
    name = fields.Str()
    data = fields.Dict()


class ResponseSchema(ma.Schema):
    speech = fields.Str()
    displayText = fields.Str(attribute='display_text')
    followupEvent = fields.Nested(FollowupEventSchema, attribute='followup_event')


last_session = None
last_id = 0


def go(input: UserInput):
    global last_id
    row = db.session.query(Question)\
        .outerjoin(Answer, Question.id == Answer.question_id) \
        .join(Property, Question.property_id == Property.id) \
        .join(PropertyType, Property.property_type_id == PropertyType.id) \
        .filter(Question.id > last_id) \
        .first()
    last_id = row.id
    pprint(questions_schema.dump(row))
    intent = row.property.property_type.intent
    print(row.value)
    return Response(input.message + row.value)
    # return Response(row.value, followup_event=FollowupEvent(intent))


def respond_to(input: UserInput) -> Response:
    global last_id
    global last_session

    if last_session != input.session_id:
        last_session = input.session_id
        last_id = 0
        print('reset session id')

    if input.action == 'smalltalk.greetings.hello':
        return go(input)

    if input.intent.startswith('question-'):
        return go(input)

    if input.action == 'start':
        return go(input)

    if input.action == 'welcome.yes':
        return go(input)

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

    return Response()


@app.route('/webhook', methods=['POST'])
def webhook():
    json = request.get_json()
    pprint(json)

    try:
        x = json['result']['fulfillment']['speech']
        if x.startswith('Unable to find'):
            raise KeyError
        message = x + '\n'
    except KeyError:
        message = ''

    session_id = json['sessionId']
    params = json['result']['parameters']
    raw = json['result']['resolvedQuery']
    action = json['result']['action']

    try:
        intent = json['result']['metadata']['intentName']
    except KeyError:
        intent = ''

    print("ACTION='{}', INTENT='{}'".format(action, intent))

    result = respond_to(UserInput(message, session_id, params, raw, action, intent))
    print(ResponseSchema().dump(result).data)

    return ResponseSchema().jsonify(result)


@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/questions')
def questions():
    rows = Question.query.all()
    return questions_schema.jsonify(rows, many=True)


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080)

