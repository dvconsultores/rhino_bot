# controllers/user_controller.py
from flask import Blueprint, request, jsonify
from services.user_service import get_all_users, get_user_by_id, create_user, update_user, delete_user

user_bp = Blueprint('user', __name__)

@user_bp.route('/users', methods=['GET'])
def get_users():
    users = get_all_users()
    return jsonify([user.__dict__ for user in users])

@user_bp.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = get_user_by_id(user_id)
    return jsonify(user.__dict__) if user else ('', 404)

@user_bp.route('/users', methods=['POST'])
def add_user():
    data = request.get_json()
    new_user = create_user(data)
    return jsonify(new_user.__dict__), 201

@user_bp.route('/users/<int:user_id>', methods=['PUT'])
def edit_user(user_id):
    data = request.get_json()
    updated_user = update_user(user_id, data)
    return jsonify(updated_user.__dict__) if updated_user else ('', 404)

@user_bp.route('/users/<int:user_id>', methods=['DELETE'])
def remove_user(user_id):
    deleted_user = delete_user(user_id)
    return jsonify(deleted_user.__dict__) if deleted_user else ('', 404)