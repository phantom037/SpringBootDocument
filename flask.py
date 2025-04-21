from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import os

app = Flask(__name__)

# Configure MySQL database
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:your_password@localhost/todo_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db = SQLAlchemy(app)
ma = Marshmallow(app)

# Todo Model
class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200))
    completed = db.Column(db.Boolean, default=False)

    def __init__(self, title, description):
        self.title = title
        self.description = description

# Todo Schema
class TodoSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Todo

todo_schema = TodoSchema()
todos_schema = TodoSchema(many=True)

# Create a Todo
@app.route('/todo', methods=['POST'])
def create_todo():
    try:
        data = request.get_json()
        if not data or 'title' not in data:
            return jsonify({'error': 'Title is required'}), 400
            
        new_todo = Todo(
            title=data['title'],
            description=data.get('description', '')
        )
        
        db.session.add(new_todo)
        db.session.commit()
        
        return todo_schema.jsonify(new_todo), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Get all Todos
@app.route('/todo', methods=['GET'])
def get_todos():
    try:
        todos = Todo.query.all()
        return todos_schema.jsonify(todos), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Get single Todo
@app.route('/todo/<id>', methods=['GET'])
def get_todo(id):
    try:
        todo = Todo.query.get(id)
        if not todo:
            return jsonify({'error': 'Todo not found'}), 404
        return todo_schema.jsonify(todo), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Update a Todo
@app.route('/todo/<id>', methods=['PUT'])
def update_todo(id):
    try:
        todo = Todo.query.get(id)
        if not todo:
            return jsonify({'error': 'Todo not found'}), 404
            
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        todo.title = data.get('title', todo.title)
        todo.description = data.get('description', todo.description)
        todo.completed = data.get('completed', todo.completed)
        
        db.session.commit()
        return todo_schema.jsonify(todo), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Delete a Todo
@app.route('/todo/<id>', methods=['DELETE'])
def delete_todo(id):
    try:
        todo = Todo.query.get(id)
        if not todo:
            return jsonify({'error': 'Todo not found'}), 404
            
        db.session.delete(todo)
        db.session.commit()
        return jsonify({'message': 'Todo deleted'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create database tables
    app.run(debug=True)
