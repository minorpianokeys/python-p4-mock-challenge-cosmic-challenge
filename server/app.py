#!/usr/bin/env python3

from models import db, Scientist, Mission, Planet
from flask_restful import Api, Resource
from flask_migrate import Migrate
from flask import Flask, make_response, jsonify, request
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)

@app.route('/')
def home():
    return ''

class Scientists(Resource):

    def get(self):
        scientists = [s.to_dict(only=("id", "name", "field_of_study")) for s in Scientist.query.all()]
        return scientists, 200
    
    def post(self):
        try:
            new_scientist = Scientist(
                name = request.json['name'],
                field_of_study = request.json['field_of_study']
            )

            db.session.add(new_scientist)
            db.session.commit()
            return new_scientist.to_dict(), 201
        
        except:
            return {"errors": ["validation errors"]}, 400

api.add_resource(Scientists, '/scientists')

class ScientistsByID(Resource):

    def get(self, id):
        scientist = Scientist.query.filter_by(id=id).first()
        if scientist:
            return scientist.to_dict(), 200  
        return {"error": "Scientist not found"}, 404
    
    def patch(self, id):
        try:
            scientist = Scientist.query.filter_by(id=id).first()
            if not scientist:
                return {"error": "Scientist not found"}, 404
            for attr in request.json:
                setattr(scientist, attr, request.json[attr])
            
            db.session.add(scientist)
            db.session.commit()
            return scientist.to_dict(), 202
        except:
            return {"errors": ["validation errors"]}, 400

    
    def delete(self, id):
        scientist = Scientist.query.filter_by(id=id).first()
        if scientist:
            db.session.delete(scientist)
            db.session.commit()
            return {}, 204
        return {"error": "Scientist not found"}, 404

api.add_resource(ScientistsByID, '/scientists/<int:id>')

class Planets(Resource):

    def get(self):
        planets = [p.to_dict(only=("id", "name", "distance_from_earth", "nearest_star")) for p in Planet.query.all()]
        return planets, 200
    
api.add_resource(Planets, '/planets')

class Missions(Resource):

    def post(self):
        try:
            new_mission = Mission(
                name = request.json['name'],
                scientist_id = request.json['scientist_id'],
                planet_id = request.json['planet_id']
            )

            db.session.add(new_mission)
            db.session.commit()
            return new_mission.to_dict(), 201
        except:
            return {"errors": ["validation errors"]}, 400
        
api.add_resource(Missions, '/missions')

if __name__ == '__main__':
    app.run(port=5555, debug=True)
