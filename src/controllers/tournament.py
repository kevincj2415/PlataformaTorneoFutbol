from flask import Blueprint, request, jsonify
from pymongo import MongoClient
from bson import ObjectId

bp = Blueprint('team', __name__)
client = MongoClient("mongodb+srv://kevincj2415:e2BhakVv76vBMD7f@cluster0.hb2dv.mongodb.net/")
db = client["torneosDB"]
teams = db["teams"]

@bp.route('/create', methods=['POST'])
def create_team():
    data = request.get_json()
    teams.insert_one(data)
    return jsonify({"message": "Equipo creado exitosamente"}), 201

@bp.route('/<id>', methods=['GET'])
def get_team(id):
    team = teams.find_one({"_id": ObjectId(id)})
    if team:
        return jsonify(team)
    return jsonify({"error": "Equipo no encontrado"}), 404
