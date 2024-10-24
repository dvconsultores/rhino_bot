# controllers/location_controller.py
from flask import Blueprint, request, jsonify
from services.location_service import get_all_locations, get_location_by_id, create_location, update_location, delete_location

location_bp = Blueprint('location', __name__)

@location_bp.route('/locations', methods=['GET'])
def get_locations():
    locations = get_all_locations()
    return jsonify([location.__dict__ for location in locations])

@location_bp.route('/locations/<int:location_id>', methods=['GET'])
def get_location(location_id):
    location = get_location_by_id(location_id)
    return jsonify(location.__dict__) if location else ('', 404)

@location_bp.route('/locations', methods=['POST'])
def add_location():
    data = request.get_json()
    new_location = create_location(data)
    return jsonify(new_location.__dict__), 201

@location_bp.route('/locations/<int:location_id>', methods=['PUT'])
def edit_location(location_id):
    data = request.get_json()
    updated_location = update_location(location_id, data)
    return jsonify(updated_location.__dict__) if updated_location else ('', 404)

@location_bp.route('/locations/<int:location_id>', methods=['DELETE'])
def remove_location(location_id):
    deleted_location = delete_location(location_id)
    return jsonify(deleted_location.__dict__) if deleted_location else ('', 404)