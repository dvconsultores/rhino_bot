# controllers/location_user_controller.py
from flask import Blueprint, request, jsonify
from services.location_user_service import get_all_location_users, get_location_user_by_id, create_location_user, update_location_user, delete_location_user

location_user_bp = Blueprint('location_user', __name__)

@location_user_bp.route('/location_users', methods=['GET'])
def get_location_users():
    location_users = get_all_location_users()
    return jsonify([location_user.__dict__ for location_user in location_users])

@location_user_bp.route('/location_users/<int:location_user_id>', methods=['GET'])
def get_location_user(location_user_id):
    location_user = get_location_user_by_id(location_user_id)
    return jsonify(location_user.__dict__) if location_user else ('', 404)

@location_user_bp.route('/location_users', methods=['POST'])
def add_location_user():
    data = request.get_json()
    new_location_user = create_location_user(data)
    return jsonify(new_location_user.__dict__), 201

@location_user_bp.route('/location_users/<int:location_user_id>', methods=['PUT'])
def edit_location_user(location_user_id):
    data = request.get_json()
    updated_location_user = update_location_user(location_user_id, data)
    return jsonify(updated_location_user.__dict__) if updated_location_user else ('', 404)

@location_user_bp.route('/location_users/<int:location_user_id>', methods=['DELETE'])
def remove_location_user(location_user_id):
    deleted_location_user = delete_location_user(location_user_id)
    return jsonify(deleted_location_user.__dict__) if deleted_location_user else ('', 404)