from flask import Blueprint, request, jsonify
from flasgger import swag_from
from services.location_service import get_all_locations, get_location_by_id, create_location, update_location, delete_location

location_bp = Blueprint('location', __name__)

@location_bp.route('/locations', methods=['GET'])
@swag_from({
    'responses': {
        200: {
            'description': 'List all locations',
            'schema': {
                'type': 'array',
                'items': {
                    'type': 'object',
                    'properties': {
                        'id': {'type': 'integer'},
                        'location': {'type': 'string'},
                        'address': {'type': 'string'},
                        'creation_date': {'type': 'string', 'format': 'date-time'}
                    }
                }
            }
        }
    }
})
def get_locations():
    """
    Get all locations
    ---
    tags:
      - Locations
    """
    locations = get_all_locations()
    return jsonify([location.to_dict() for location in locations])

@location_bp.route('/locations/<int:location_id>', methods=['GET'])
@swag_from({
    'parameters': [
        {
            'name': 'location_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'ID of the location to retrieve'
        }
    ],
    'responses': {
        200: {
            'description': 'Details of the location',
            'schema': {
                'type': 'object',
                'properties': {
                    'id': {'type': 'integer'},
                    'location': {'type': 'string'},
                    'address': {'type': 'string'},
                    'creation_date': {'type': 'string', 'format': 'date-time'}
                }
            }
        },
        404: {'description': 'Location not found'}
    }
})
def get_location(location_id):
    """
    Get a location by ID
    ---
    tags:
      - Locations
    """
    location = get_location_by_id(location_id)
    return jsonify(location.to_dict()) if location else ('', 404)

@location_bp.route('/locations', methods=['POST'])
@swag_from({
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'schema': {
                'type': 'object',
                'properties': {
                    'location': {'type': 'string'},
                    'address': {'type': 'string'}
                },
                'required': ['location', 'address']
            }
        }
    ],
    'responses': {
        201: {
            'description': 'Location created successfully',
            'schema': {
                'type': 'object',
                'properties': {
                    'id': {'type': 'integer'},
                    'location': {'type': 'string'},
                    'address': {'type': 'string'},
                    'creation_date': {'type': 'string', 'format': 'date-time'}
                }
            }
        }
    }
})
def add_location():
    """
    Add a new location
    ---
    tags:
      - Locations
    """
    data = request.get_json()
    new_location = create_location(data)
    return jsonify(new_location.to_dict()), 201

@location_bp.route('/locations/<int:location_id>', methods=['PUT'])
@swag_from({
    'parameters': [
        {
            'name': 'location_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'ID of the location to update'
        },
        {
            'name': 'body',
            'in': 'body',
            'schema': {
                'type': 'object',
                'properties': {
                    'location': {'type': 'string'},
                    'address': {'type': 'string'}
                },
                'required': ['location', 'address']
            }
        }
    ],
    'responses': {
        200: {
            'description': 'Location updated successfully',
            'schema': {
                'type': 'object',
                'properties': {
                    'id': {'type': 'integer'},
                    'location': {'type': 'string'},
                    'address': {'type': 'string'},
                    'creation_date': {'type': 'string', 'format': 'date-time'}
                }
            }
        },
        404: {'description': 'Location not found'}
    }
})
def edit_location(location_id):
    """
    Update an existing location
    ---
    tags:
      - Locations
    """
    data = request.get_json()
    updated_location = update_location(location_id, data)
    return jsonify(updated_location.to_dict()) if updated_location else ('', 404)

@location_bp.route('/locations/<int:location_id>', methods=['DELETE'])
@swag_from({
    'parameters': [
        {
            'name': 'location_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'ID of the location to delete'
        }
    ],
    'responses': {
        200: {
            'description': 'Location deleted successfully',
            'schema': {
                'type': 'object',
                'properties': {
                    'id': {'type': 'integer'},
                    'location': {'type': 'string'},
                    'address': {'type': 'string'},
                    'creation_date': {'type': 'string', 'format': 'date-time'}
                }
            }
        },
        404: {'description': 'Location not found'}
    }
})
def remove_location(location_id):
    """
    Delete a location
    ---
    tags:
      - Locations
    """
    deleted_location = delete_location(location_id)
    return jsonify(deleted_location.to_dict()) if deleted_location else ('', 404)
