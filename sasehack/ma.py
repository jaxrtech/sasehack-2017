from flask import Flask, jsonify
from flask_marshmallow import Marshmallow

app = Flask(__name__)
ma = Marshmallow(app)

from your_orm import Model, Column, Integer, String, DateTime

class User(Model):
    email = Column(String)
    password = Column(String)
    date_created = Column(DateTime, auto_now_add=True)

class UserSchema(ma.Schema):
    class Meta:
        # Fields to expose
        fields = ('email', 'date_created', '_links')
    # Smart hyperlinking
    _links = ma.Hyperlinks({
        'self': ma.URLFor('author_detail', id='<id>'),
        'collection': ma.URLFor('authors')
    })

user_schema = UserSchema()
users_schema = UserSchema(many=True)

@app.route('/api/users/')
def users():
    all_users = User.all()
    result = users_schema.dump(all_users)
    return jsonify(result.data)
    # OR
    # return user_schema.jsonify(all_users)

@app.route('/api/users/<id>')
def user_detail(id):
    user = User.get(id)
    return user_schema.jsonify(user)
# {
#     "email": "fred@queen.com",
#     "date_created": "Fri, 25 Apr 2014 06:02:56 -0000",
#     "_links": {
#         "self": "/api/authors/42",
#         "collection": "/api/authors/"
#     }
# }