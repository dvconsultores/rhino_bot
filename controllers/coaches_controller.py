from flask import Blueprint, jsonify, request
from services.coaches_service import CoachesService
from flasgger import swag_from

coach_bp = Blueprint('coach', __name__)

@coach_bp.route('/coaches', methods=['POST'])
@swag_from({
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'schema': {
                'type': 'object',
                'properties': {
                    'cedula': {'type': 'string'},
                    'names': {'type': 'string'},
                    'location_id': {'type': 'integer'}
                },
                'required': ['cedula', 'names', 'location_id']
            }
        }
    ],
    'responses': {
        201: {
            'description': 'Coach created successfully',
            'schema': {
                'type': 'object',
                'properties': {
                    'id': {'type': 'integer'},
                    'cedula': {'type': 'string'},
                    'names': {'type': 'string'},
                    'location_id': {'type': 'integer'},
                    'location_name': {'type': 'string'}
                }
            }
        }
    }
})
def create_coach():
    data = request.get_json()
    new_coach = CoachesService.create_coach(data['cedula'], data['names'], data['location_id'])
    return jsonify(new_coach.to_dict()), 201

@coach_bp.route('/coaches/<int:coach_id>', methods=['GET'])
@swag_from({
    'parameters': [
        {
            'name': 'coach_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'ID of the coach to retrieve'
        }
    ],
    'responses': {
        200: {
            'description': 'Coach retrieved successfully',
            'schema': {
                'type': 'object',
                'properties': {
                    'id': {'type': 'integer'},
                    'cedula': {'type': 'string'},
                    'names': {'type': 'string'},
                    'location_id': {'type': 'integer'},
                    'location_name': {'type': 'string'}
                }
            }
        },
        404: {'description': 'Coach not found'}
    }
})
def get_coach(coach_id):
    coach = CoachesService.get_coach_by_id(coach_id)
    if coach:
        return jsonify(coach.to_dict())
    else:
        return jsonify({'error': 'Coach not found'}), 404

@coach_bp.route('/coaches', methods=['GET'])
@swag_from({
    'responses': {
        200: {
            'description': 'List all coaches',
            'schema': {
                'type': 'array',
                'items': {
                    'type': 'object',
                    'properties': {
                        'id': {'type': 'integer'},
                        'cedula': {'type': 'string'},
                        'names': {'type': 'string'},
                        'location_id': {'type': 'integer'},
                        'location_name': {'type': 'string'}
                    }
                }
            }
        }
    }
})
def get_all_coaches():
    coaches = CoachesService.get_all_coaches()
    return jsonify([coach.to_dict() for coach in coaches])

@coach_bp.route('/coaches/<int:coach_id>', methods=['PUT'])
@swag_from({
    'parameters': [
        {
            'name': 'coach_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'ID of the coach to update'
        },
        {
            'name': 'body',
            'in': 'body',
            'schema': {
                'type': 'object',
                'properties': {
                    'cedula': {'type': 'string'},
                    'names': {'type': 'string'},
                    'location_id': {'type': 'integer'}
                }
            }
        }
    ],
    'responses': {
        200: {
            'description': 'Coach updated successfully',
            'schema': {
                'type': 'object',
                'properties': {
                    'id': {'type': 'integer'},
                    'cedula': {'type': 'string'},
                    'names': {'type': 'string'},
                    'location_id': {'type': 'integer'},
                    'location_name': {'type': 'string'}
                }
            }
        },
        404: {'description': 'Coach not found'}
    }
})
def update_coach(coach_id):
    data = request.get_json()
    updated_coach = CoachesService.update_coach(coach_id, data.get('cedula'), data.get('names'), data.get('location_id'))
    if updated_coach:
        return jsonify(updated_coach.to_dict())
    else:
        return jsonify({'error': 'Coach not found'}), 404

@coach_bp.route('/coaches/<int:coach_id>', methods=['DELETE'])
@swag_from({
    'parameters': [
        {
            'name': 'coach_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'ID of the coach to delete'
        }
    ],
    'responses': {
        200: {'description': 'Coach deleted successfully'},
        404: {'description': 'Coach not found'}
    }
})
def delete_coach(coach_id):
    deleted_coach = CoachesService.delete_coach(coach_id)
    if deleted_coach:
        return jsonify(deleted_coach.to_dict())
    else:
        return jsonify({'error': 'Coach not found'}), 404