import requests
from flask import Flask, request, jsonify
from fuzzywuzzy import fuzz
from models import db, Item
from secrets_1 import LLAMA_API_KEY

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///items.db'
db.init_app(app)

with app.app_context():
    db.create_all()

LLAMA_API_URL = "https://pkosc7r8nk-vpce-0e881c3ec15437336.execute-api.eu-west-1.amazonaws.com/llama-3-8b"

@app.route('/items', methods=['POST'])
def add_item():
    data = request.get_json()
    new_item = Item(
        tags=data['tags'],
        summary=data['summary'],
        details=data['details'],
        url=data['url'],
        related=data.get('related'),
        priority=data['priority']
    )
    db.session.add(new_item)
    db.session.commit()
    return jsonify({'message': 'Item created successfully'}), 201

@app.route('/items', methods=['GET'])
def get_items():
    items = Item.query.all()
    return jsonify([{
        'id': item.id,
        'tags': item.tags,
        'summary': item.summary,
        'details': item.details,
        'url': item.url,
        'related': item.related,
        'priority': item.priority
    } for item in items])

@app.route('/items/<int:id>', methods=['GET'])
def get_item(id):
    item = Item.query.get_or_404(id)
    return jsonify({
        'id': item.id,
        'tags': item.tags,
        'summary': item.summary,
        'details': item.details,
        'url': item.url,
        'related': item.related,
        'priority': item.priority
    })

@app.route('/items/<int:id>', methods=['PUT'])
def update_item(id):
    data = request.get_json()
    item = Item.query.get_or_404(id)
    item.tags = data['tags']
    item.summary = data['summary']
    item.details = data['details']
    item.url = data['url']
    item.related = data.get('related')
    item.priority = data['priority']
    db.session.commit()
    return jsonify({'message': 'Item updated successfully'})

@app.route('/items/<int:id>', methods=['DELETE'])
def delete_item(id):
    item = Item.query.get_or_404(id)
    db.session.delete(item)
    db.session.commit()
    return jsonify({'message': 'Item deleted successfully'})

@app.route('/query', methods=['POST'])
def query_items():
    data = request.get_json()
    subject = data['subject']
    body = data['body']

    # Query Llama-3 API
    response = requests.post(
        f"{LLAMA_API_URL}/generate",
        json={
            "inputs": f"<|begin_of_text|>{subject} {body}<|eot_id|>",
            "parameters": {
                "max_tokens": 128
            }
        },
        headers={
            "Content-Type": "application/json",
            "x-api-key": LLAMA_API_KEY
        }
    )

    if response.status_code != 200:
        print("Error:", response.status_code, response.text)
        return jsonify({'message': 'Failed to generate query context'}), response.status_code

    response_data = response.json()
    query_text = response_data.get('generated_text', '')

    # Query the database with fuzzy matching
    items = Item.query.all()
    matched_items = []
    for item in items:
        subject_match = fuzz.partial_ratio(subject.lower(), item.summary.lower())
        body_match = fuzz.partial_ratio(body.lower(), item.details.lower())
        if subject_match > 70 and body_match > 70:  # Adjust the threshold as needed
            matched_items.append(item)

    if matched_items:
        return jsonify([{
            'id': item.id,
            'tags': item.tags,
            'summary': item.summary,
            'details': item.details,
            'url': item.url,
            'related': item.related,
            'priority': item.priority,
            'message': "Success"
        } for item in matched_items])
    else:
        return jsonify({'message': 'No related records found'}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
