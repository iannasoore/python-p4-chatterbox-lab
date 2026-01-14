from flask import Flask, request, make_response, jsonify
from flask_cors import CORS
from flask_migrate import Migrate

from models import db, Message

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

CORS(app)
migrate = Migrate(app, db)

db.init_app(app)

with app.app_context():
    db.create_all()

    seed = Message.query.filter_by(body="Seed message", username="Seed").first()
    if seed is None:
        db.session.add(Message(body="Seed message", username="Seed"))
        db.session.commit()


def message_to_dict(message: Message):
    return {
        "id": message.id,
        "body": message.body,
        "username": message.username,
        "created_at": message.created_at.isoformat() if message.created_at else None,
    }

@app.route('/messages', methods=['GET', 'POST'])
def messages():
    if request.method == 'GET':
        messages = Message.query.all()
        return make_response(jsonify([message_to_dict(m) for m in messages]), 200)

    data = request.get_json(silent=True) or {}
    message = Message(
        body=data.get('body'),
        username=data.get('username'),
    )
    db.session.add(message)
    db.session.commit()

    return make_response(jsonify(message_to_dict(message)), 201)

@app.route('/messages/<int:id>', methods=['PATCH', 'DELETE'])
def messages_by_id(id):
    message = Message.query.get_or_404(id)

    if request.method == 'PATCH':
        data = request.get_json(silent=True) or {}
        if 'body' in data:
            message.body = data['body']

        db.session.add(message)
        db.session.commit()
        return make_response(jsonify(message_to_dict(message)), 200)

    db.session.delete(message)
    db.session.commit()
    return make_response('', 204)

if __name__ == '__main__':
    app.run(port=5555)
