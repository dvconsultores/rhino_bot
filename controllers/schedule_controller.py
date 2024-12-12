from flask import Blueprint, request, jsonify
from flasgger import swag_from
from services.schedule_service import get_all_schedules, get_schedule_by_id, create_schedule, update_schedule as update_schedule_controller , delete_schedule as delete_schedule_service

# Create the Blueprint for schedules
schedule_bp = Blueprint('schedule', __name__)

@schedule_bp.route('/schedules', methods=['GET'])
@swag_from({
    'tags': ['Schedules'],
    'responses': {
        200: {
            'description': 'A list of schedules',
            'schema': {
                'type': 'array',
                'items': {
                    'type': 'object',
                    'properties': {
                        'id': {'type': 'integer'},
                        'location_id': {'type': 'integer'},
                        'days': {'type': 'string'},
                        'time_init': {'type': 'string'},
                        'creation_date': {'type': 'string', 'format': 'date-time'}
                    }
                }
            }
        }
    }
})
def get_schedules():
    """
    Fetch all schedules.
    """
    schedules = get_all_schedules()
    return jsonify([schedule.to_dict() for schedule in schedules])

@schedule_bp.route('/schedules/<int:schedule_id>', methods=['GET'])
@swag_from({
    'tags': ['Schedules'],
    'summary': 'Get a schedule by ID',
    'description': 'Retrieve a schedule by its ID.',
    'parameters': [
        {
            'name': 'schedule_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'The ID of the schedule to retrieve'
        }
    ],
    'responses': {
        200: {
            'description': 'A schedule',
            'schema': {
                'type': 'object',
                'properties': {
                    'id': {'type': 'integer'},
                    'location_id': {'type': 'integer'},
                    'days': {'type': 'string'},
                    'time_init': {'type': 'string'},
                    'creation_date': {'type': 'string', 'format': 'date-time'}
                }
            }
        },
        404: {
            'description': 'Schedule not found'
        }
    }
})
def get_schedule(schedule_id):
    """
    Fetch a specific schedule by its ID.
    """
    schedule = get_schedule_by_id(schedule_id)
    return jsonify(schedule.to_dict()) if schedule else ('', 404)

@schedule_bp.route('/schedules', methods=['POST'])
@swag_from({
    'tags': ['Schedules'],
    'summary': 'Create a new schedule',
    'description': 'Create a new schedule with the provided data.',
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'location_id': {'type': 'integer'},
                    'days': {'type': 'string'},
                    'time_init': {'type': 'string'}
                }
            }
        }
    ],
    'responses': {
        201: {
            'description': 'Schedule created',
            'schema': {
                'type': 'object',
                'properties': {
                    'id': {'type': 'integer'},
                    'location_id': {'type': 'integer'},
                    'days': {'type': 'string'},
                    'time_init': {'type': 'string'},
                    'creation_date': {'type': 'string', 'format': 'date-time'}
                }
            }
        }
    }
})
def add_schedule():
    """
    Add a new schedule.
    """
    data = request.get_json()
    new_schedule = create_schedule(data)
    return jsonify(new_schedule.to_dict()), 201

@schedule_bp.route('/schedules/<int:schedule_id>', methods=['PUT'])
@swag_from({
    'tags': ['Schedules'],
    'summary': 'Update a schedule',
    'description': 'Update an existing schedule with the provided data.',
    'parameters': [
        {
            'name': 'schedule_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'The ID of the schedule to update'
        },
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'location_id': {'type': 'integer'},
                    'days': {'type': 'string'},
                    'time_init': {'type': 'string'}
                }
            }
        }
    ],
    'responses': {
        200: {
            'description': 'Schedule updated',
            'schema': {
                'type': 'object',
                'properties': {
                    'id': {'type': 'integer'},
                    'location_id': {'type': 'integer'},
                    'days': {'type': 'string'},
                    'time_init': {'type': 'string'},
                    'creation_date': {'type': 'string', 'format': 'date-time'}
                }
            }
        },
        404: {
            'description': 'Schedule not found'
        }
    }
})
def edit_schedule(schedule_id):
    """
    Update an existing schedule by its ID.
    """
    data = request.get_json()
    updated_schedule = update_schedule_controller(schedule_id, data)
    return jsonify(updated_schedule.to_dict()) if updated_schedule else ('', 404)

@schedule_bp.route('/schedules/<int:schedule_id>', methods=['DELETE'])
@swag_from({
    'tags': ['Schedules'],
    'summary': 'Delete a schedule',
    'description': 'Delete a schedule by its ID.',
    'parameters': [
        {
            'name': 'schedule_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'The ID of the schedule to delete'
        }
    ],
    'responses': {
        200: {
            'description': 'Schedule deleted',
            'schema': {
                'type': 'object',
                'properties': {
                    'id': {'type': 'integer'},
                    'location_id': {'type': 'integer'},
                    'days': {'type': 'string'},
                    'time_init': {'type': 'string'},
                    'creation_date': {'type': 'string', 'format': 'date-time'}
                }
            }
        },
        404: {
            'description': 'Schedule not found'
        }
    }
})
def delete_schedule(schedule_id):
    """
    Delete a schedule by its ID.
    """
    deleted_schedule = delete_schedule_service(schedule_id)  # Use the renamed service function
    return jsonify(deleted_schedule.to_dict()) if deleted_schedule else ('', 404)
