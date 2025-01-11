from flask import Blueprint, request, jsonify
from flasgger import swag_from
from services.attendance_service import AttendanceService

# Create a Blueprint for attendance
attendance_bp = Blueprint('attendance', __name__)

@attendance_bp.route('/attendances', methods=['POST'])
@swag_from({
    'tags': ['Attendance'],
    'summary': 'Create a new attendance record',
    'description': 'Creates a new attendance record for a coach, location, and user on a specific date.',
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'coach_id': {'type': 'integer'},
                    'location_id': {'type': 'integer'},
                    'user_id': {'type': 'integer'},
                    'date': {'type': 'string', 'format': 'date'}
                },
                'required': ['coach_id', 'location_id', 'user_id', 'date']
            }
        }
    ],
    'responses': {
        201: {
            'description': 'Attendance created successfully',
            'schema': {
                'type': 'object',
                'properties': {
                    'id': {'type': 'integer'},
                    'coach_id': {'type': 'integer'},
                    'location_id': {'type': 'integer'},
                    'user_id': {'type': 'integer'},
                    'date': {'type': 'string', 'format': 'date'}
                }
            }
        },
        400: {'description': 'Invalid input'},
        500: {'description': 'Server error'}
    }
})
def create_attendance():
    """Create a new attendance record."""
    data = request.get_json()
    result = AttendanceService.create_attendance(data)
    if isinstance(result, tuple):
        return jsonify(result[0]), result[1]
    return jsonify(result.to_dict()), 201


@attendance_bp.route('/attendances/<int:attendance_id>', methods=['GET'])
@swag_from({
    'tags': ['Attendance'],
    'summary': 'Get an attendance record by ID',
    'description': 'Retrieve an attendance record by its unique ID.',
    'parameters': [
        {
            'name': 'attendance_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'ID of the attendance record'
        }
    ],
    'responses': {
        200: {
            'description': 'Attendance record retrieved successfully',
            'schema': {
                'type': 'object',
                'properties': {
                    'id': {'type': 'integer'},
                    'coach_id': {'type': 'integer'},
                    'location_id': {'type': 'integer'},
                    'user_id': {'type': 'integer'},
                    'date': {'type': 'string', 'format': 'date'}
                }
            }
        },
        404: {'description': 'Attendance not found'}
    }
})
def get_attendance(attendance_id):
    """Retrieve an attendance record by ID."""
    attendance = AttendanceService.get_attendance_by_id(attendance_id)
    if attendance:
        return jsonify(attendance.to_dict())
    return jsonify({'error': 'Attendance not found'}), 404


@attendance_bp.route('/attendances', methods=['GET'])
@swag_from({
    'tags': ['Attendance'],
    'summary': 'List all attendance records',
    'description': 'Retrieve a list of all attendance records.',
    'responses': {
        200: {
            'description': 'List of attendance records retrieved successfully',
            'schema': {
                'type': 'array',
                'items': {
                    'type': 'object',
                    'properties': {
                        'id': {'type': 'integer'},
                        'coach_id': {'type': 'integer'},
                        'location_id': {'type': 'integer'},
                        'user_id': {'type': 'integer'},
                        'date': {'type': 'string', 'format': 'date'}
                    }
                }
            }
        }
    }
})
def list_attendances():
    """Retrieve a list of all attendance records."""
    attendances = AttendanceService.list_all_attendances()
    return jsonify([attendance.to_dict() for attendance in attendances])


@attendance_bp.route('/attendances/<int:attendance_id>', methods=['PUT'])
@swag_from({
    'tags': ['Attendance'],
    'summary': 'Update an attendance record',
    'description': 'Update an existing attendance record by its ID.',
    'parameters': [
        {
            'name': 'attendance_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'ID of the attendance record to update'
        },
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'coach_id': {'type': 'integer'},
                    'location_id': {'type': 'integer'},
                    'user_id': {'type': 'integer'},
                    'date': {'type': 'string', 'format': 'date'}
                }
            }
        }
    ],
    'responses': {
        200: {
            'description': 'Attendance updated successfully',
            'schema': {
                'type': 'object',
                'properties': {
                    'id': {'type': 'integer'},
                    'coach_id': {'type': 'integer'},
                    'location_id': {'type': 'integer'},
                    'user_id': {'type': 'integer'},
                    'date': {'type': 'string', 'format': 'date'}
                }
            }
        },
        404: {'description': 'Attendance not found'},
        500: {'description': 'Server error'}
    }
})
def update_attendance(attendance_id):
    """Update an attendance record."""
    data = request.get_json()
    result = AttendanceService.update_attendance(attendance_id, data)
    if isinstance(result, tuple):
        return jsonify(result[0]), result[1]
    return jsonify(result.to_dict()), 200


@attendance_bp.route('/attendances/<int:attendance_id>', methods=['DELETE'])
@swag_from({
    'tags': ['Attendance'],
    'summary': 'Delete an attendance record',
    'description': 'Delete an attendance record by its ID.',
    'parameters': [
        {
            'name': 'attendance_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'ID of the attendance record to delete'
        }
    ],
    'responses': {
        200: {
            'description': 'Attendance deleted successfully',
            'schema': {
                'type': 'object',
                'properties': {
                    'id': {'type': 'integer'},
                    'coach_id': {'type': 'integer'},
                    'location_id': {'type': 'integer'},
                    'user_id': {'type': 'integer'},
                    'date': {'type': 'string', 'format': 'date'}
                }
            }
        },
        404: {'description': 'Attendance not found'}
    }
})
def delete_attendance(attendance_id):
    """Delete an attendance record."""
    result = AttendanceService.delete_attendance(attendance_id)
    if isinstance(result, tuple):
        return jsonify(result[0]), result[1]
    return jsonify(result.to_dict()), 200
