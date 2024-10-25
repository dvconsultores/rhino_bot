from flask import Blueprint, request, jsonify
from flasgger import swag_from
from models.users import User, UserType, Status
from db import db

user_bp = Blueprint('user', __name__)

@user_bp.route('/users', methods=['GET'])
@swag_from({
    'tags': ['Users'],
    'summary': 'Get all users',
    'description': 'Retrieve a list of all users.',
    'responses': {
        200: {
            'description': 'A list of users',
            'schema': {
                'type': 'array',
                'items': {
                    'type': 'object',
                    'properties': {
                        'id': {'type': 'integer'},
                        'name': {'type': 'string'},
                        'lastname': {'type': 'string'},
                        'cedula': {'type': 'integer'},
                        'email': {'type': 'string'},
                        'date_of_birth': {'type': 'string', 'format': 'date'},
                        'phone': {'type': 'integer'},
                        'instagram': {'type': 'string'},
                        'type': {'type': 'string'},
                        'status': {'type': 'string'},
                        'creation_date': {'type': 'string', 'format': 'date-time'},
                        'telegram_id': {'type': 'integer'}
                    }
                }
            }
        }
    }
})
def get_users():
    users = User.query.all()
    return jsonify([user.to_dict() for user in users])

@user_bp.route('/users/<int:user_id>', methods=['GET'])
@swag_from({
    'tags': ['Users'],
    'summary': 'Get a user by ID',
    'description': 'Retrieve a user by their ID.',
    'parameters': [
        {
            'name': 'user_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'The ID of the user'
        }
    ],
    'responses': {
        200: {
            'description': 'A user',
            'schema': {
                'type': 'object',
                'properties': {
                    'id': {'type': 'integer'},
                    'name': {'type': 'string'},
                    'lastname': {'type': 'string'},
                    'cedula': {'type': 'integer'},
                    'email': {'type': 'string'},
                    'date_of_birth': {'type': 'string', 'format': 'date'},
                    'phone': {'type': 'integer'},
                    'instagram': {'type': 'string'},
                    'type': {'type': 'string'},
                    'status': {'type': 'string'},
                    'creation_date': {'type': 'string', 'format': 'date-time'},
                    'telegram_id': {'type': 'integer'}
                }
            }
        },
        404: {
            'description': 'User not found'
        }
    }
})
def get_user(user_id):
    user = User.query.get(user_id)
    return jsonify(user.to_dict()) if user else ('', 404)

@user_bp.route('/users', methods=['POST'])
@swag_from({
    'tags': ['Users'],
    'summary': 'Create a new user',
    'description': 'Create a new user with the provided data.',
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'name': {'type': 'string'},
                    'lastname': {'type': 'string'},
                    'cedula': {'type': 'integer'},
                    'email': {'type': 'string'},
                    'date_of_birth': {'type': 'string', 'format': 'date'},
                    'phone': {'type': 'integer'},
                    'instagram': {'type': 'string'},
                    'type': {'type': 'string', 'enum': [e.value for e in UserType]},
                    'status': {'type': 'string', 'enum': [e.value for e in Status]},
                    'telegram_id': {'type': 'integer'}
                }
            }
        }
    ],
    'responses': {
        201: {
            'description': 'User created',
            'schema': {
                'type': 'object',
                'properties': {
                    'id': {'type': 'integer'},
                    'name': {'type': 'string'},
                    'lastname': {'type': 'string'},
                    'cedula': {'type': 'integer'},
                    'email': {'type': 'string'},
                    'date_of_birth': {'type': 'string', 'format': 'date'},
                    'phone': {'type': 'integer'},
                    'instagram': {'type': 'string'},
                    'type': {'type': 'string'},
                    'status': {'type': 'string'},
                    'creation_date': {'type': 'string', 'format': 'date-time'},
                    'telegram_id': {'type': 'integer'}
                }
            }
        }
    }
})
def create_user():
    data = request.get_json()
    new_user = User(**data)
    db.session.add(new_user)
    db.session.commit()
    return jsonify(new_user.to_dict()), 201

@user_bp.route('/users/<int:user_id>', methods=['PUT'])
@swag_from({
    'tags': ['Users'],
    'summary': 'Update a user',
    'description': 'Update an existing user with the provided data.',
    'parameters': [
        {
            'name': 'user_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'The ID of the user'
        },
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'name': {'type': 'string'},
                    'lastname': {'type': 'string'},
                    'cedula': {'type': 'integer'},
                    'email': {'type': 'string'},
                    'date_of_birth': {'type': 'string', 'format': 'date'},
                    'phone': {'type': 'integer'},
                    'instagram': {'type': 'string'},
                    'type': {'type': 'string', 'enum': [e.value for e in UserType]},
                    'status': {'type': 'string', 'enum': [e.value for e in Status]},
                    'telegram_id': {'type': 'integer'}
                }
            }
        }
    ],
    'responses': {
        200: {
            'description': 'User updated',
            'schema': {
                'type': 'object',
                'properties': {
                    'id': {'type': 'integer'},
                    'name': {'type': 'string'},
                    'lastname': {'type': 'string'},
                    'cedula': {'type': 'integer'},
                    'email': {'type': 'string'},
                    'date_of_birth': {'type': 'string', 'format': 'date'},
                    'phone': {'type': 'integer'},
                    'instagram': {'type': 'string'},
                    'type': {'type': 'string'},
                    'status': {'type': 'string'},
                    'creation_date': {'type': 'string', 'format': 'date-time'},
                    'telegram_id': {'type': 'integer'}
                }
            }
        },
        404: {
            'description': 'User not found'
        }
    }
})
def update_user(user_id):
    data = request.get_json()
    user = User.query.get(user_id)
    if user:
        for key, value in data.items():
            setattr(user, key, value)
        db.session.commit()
        return jsonify(user.to_dict())
    else:
        return ('', 404)

@user_bp.route('/users/<int:user_id>', methods=['DELETE'])
@swag_from({
    'tags': ['Users'],
    'summary': 'Delete a user',
    'description': 'Delete a user by their ID.',
    'parameters': [
        {
            'name': 'user_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'The ID of the user'
        }
    ],
    'responses': {
        200: {
            'description': 'User deleted',
            'schema': {
                'type': 'object',
                'properties': {
                    'id': {'type': 'integer'},
                    'name': {'type': 'string'},
                    'lastname': {'type': 'string'},
                    'cedula': {'type': 'integer'},
                    'email': {'type': 'string'},
                    'date_of_birth': {'type': 'string', 'format': 'date'},
                    'phone': {'type': 'integer'},
                    'instagram': {'type': 'string'},
                    'type': {'type': 'string'},
                    'status': {'type': 'string'},
                    'creation_date': {'type': 'string', 'format': 'date-time'},
                    'telegram_id': {'type': 'integer'}
                }
            }
        },
        404: {
            'description': 'User not found'
        }
    }
})
def delete_user(user_id):
    user = User.query.get(user_id)
    if user:
        db.session.delete(user)
        db.session.commit()
        return jsonify(user.to_dict())
    else:
        return ('', 404)