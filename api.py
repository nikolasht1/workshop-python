from asyncio.proactor_events import _ProactorBasePipeTransport
import os

from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
import dotenv
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
from marshmallow import Schema, fields

dotenv.load_dotenv()

db_user = os.environ.get('DB_USERNAME')
db_pass = os.environ.get('DB_PASSWORD')
db_hostname = os.environ.get('DB_HOSTNAME')
db_name = os.environ.get('DB_NAME')

DB_URI = 'mysql+pymysql://{db_username}:{db_password}@{db_host}/{database}'.format(db_username=db_user, db_password=db_pass, db_host=db_hostname, database=db_name)

engine = create_engine(DB_URI, echo=True)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DB_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Student(db.Model):
    __tablename__ = "student"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    age = db.Column(db.Integer, nullable=False)
    cellphone = db.Column(db.String(13), unique=True, nullable=False)

    @classmethod
    def get_all(cls):
        return cls.query.all()

    @classmethod
    def get_by_id(cls, id):
        return cls.query.get_or_404(id)

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

class StudentSchema(Schema):
    id = fields.Integer()
    name = fields.Str()
    email = fields.Str()
    age = fields.Integer()
    cellphone = fields.Str()  
    
class ApiDoc:
    method = ""
    endpoint = ""
    description = ""
    responseCode = 200

    def __init__(self, method, endpoint, description):
        self.method = method
        self.endpoint = endpoint
        self.description = description

    def getAllEndpointsDoc():
        return [ApiDoc("GET", "/api", "Api documentation").toJSON(),
                ApiDoc("GET", "/api/students", "Retrieve all students").toJSON(),
                ApiDoc("GET", "/api/students/{id}", "Retrieve student by id").toJSON(),
                ApiDoc("POST", "/api/students/create", "Create new student").toJSON(),
                ApiDoc("PATCH", "/api/students/modify/{id}", "Modify student name,age,email and cellphone by student id").toJSON(),
                ApiDoc("PUT", "/api/students/change/{id}", "Modify all student fields").toJSON(),
                ApiDoc("DELETE", "/api/deleteStudent/{id}", "Delete student by id").toJSON()]

    def toJSON(self):
        return '{"method": ' + str(self.method) + \
            ', "endpoint": ' + str(self.endpoint) + \
            ', "responseCode": ' + str(self.responseCode) + \
            ', "description": ' + str(self.description) + '}'

    

@app.route('/api', methods=['GET'])
def api_main():
    return jsonify(ApiDoc.getAllEndpointsDoc()), 200


@app.route('/api/students', methods=['GET'])
def get_all_students():
    students = Student.get_all()
    student_list = StudentSchema(many=True)
    response = student_list.dump(students)
    return jsonify(response), 200

@app.route('/api/students/<int:id>', methods = ['GET'])
def get_student(id):
    student_info = Student.get_by_id(id)
    serializer = StudentSchema()
    response = serializer.dump(student_info)
    return jsonify(response), 200

@app.route('/api/students/create', methods = ['POST'])
def add_student():
    json_data = request.get_json()
    new_student = Student(
        name=json_data.get('name'),
        email=json_data.get('email'),
        age=json_data.get('age'),
        cellphone=json_data.get('cellphone')
    )
    new_student.save()
    serializer = StudentSchema()
    data = serializer.dump(new_student)
    return jsonify(data), 200

@app.route('/api/students/modify/<int:id>', methods = ['PATCH'])
def modify_student(id):
    student = Student.get_by_id(id)
    student_json = request.get_json()
    name = student_json.get("name"),
    email = student_json.get("email"),
    age = student_json.get("age"),
    cellphone = student_json.get("cellphone")

    if name:
        student.name = name
    if email:
        student.email = email
    if age:
        student.age = age
    if cellphone:
        student.cellphone = cellphone            

    student.save()
    serializer = StudentSchema()
    data = serializer.dump(student)
    return jsonify(data), 200

@app.route('/api/deleteStudent/<int:id>', methods = ['DELETE'])
def delete_student(id):
    student = Student.get_by_id(id)
    student.delete()
    return '<p>Item deleted!</p>', 200

@app.route('/api/students/change/<int:id>', methods = ['PUT'])
def change_student(id):
    student = Student.get_by_id(id)
    json_data = request.get_json()

    student.name=json_data.get('name'),
    student.email=json_data.get('email'),
    student.age=json_data.get('age'),
    student.cellphone=json_data.get('cellphone')

    student.save()
    
    serializer = StudentSchema()
    data = serializer.dump(student)
    return '<p>Item changed!</p>', 200


@app.route('/api/health-check/ok', methods = ['GET'])
def health_check():
    return '<p>Service is helthy!</p>', 200  
      

@app.route('/api/health-check/bad', methods = ['GET'])
def sevice_no_helthy():
    return '<p>Service is  not helthy!</p>', 500     


if __name__ == '__main__':
    if not database_exists(engine.url):
        create_database(engine.url)
    db.create_all()
    app.run(host="0.0.0.0",debug=True)