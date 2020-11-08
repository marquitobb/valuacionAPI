import os
import json
from flask import Flask, request, jsonify
from flask_restful import Resource, Api
from flask_sqlalchemy import SQLAlchemy

from flask_marshmallow import Marshmallow

from serializers import AlchemyEncoder

app = Flask(__name__)
#api = Api(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://{}:{}@{}/{}'.format(
    os.getenv('DB_USER', 'flask'),
    os.getenv('DB_PASSWORD', ''),
    os.getenv('DB_HOST', 'mysql'),
    os.getenv('DB_NAME', 'flask')
)
db = SQLAlchemy(app)
ma = Marshmallow(app)


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(70), unique=True)
    precio= db.Column(db.Integer)

    def __init__(self, nombre, precio):
        self.nombre = nombre
        self.precio = precio

db.create_all()

class TaskSchema(ma.Schema):
    class Meta:
        fields = ('id', 'nombre', 'precio')

task_schema = TaskSchema()
tasks_schema = TaskSchema(many=True)

@app.route('/tasks', methods=['POST'])
def create_task():

    nombre = request.json['nombre']
    precio = request.json['precio']
    new_task = Task(nombre, precio)
    db.session.add(new_task)
    db.session.commit()
    print(request.json)

    return task_schema.jsonify(new_task)

@app.route('/tasks', methods=['GET'])
def get_task():
    all_tasks = Task.query.all()
    result = tasks_schema.dump(all_tasks)
    return jsonify(result)

@app.route('/ver/<id>', methods=['GET'])
def get_task_id(id):
    task = Task.query.get(id)
    return task_schema.jsonify(task)


@app.route('/', methods=['GET'])
def index():
    return 'Welcome api evaluos'


if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=False)
