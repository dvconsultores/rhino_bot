# controllers/user_controller.py

from flask import Blueprint, request, jsonify
from flasgger import swag_from
from services.user_service import (
    get_all_users,
    get_user_by_id,
    get_user_by_telegram_id,
    create_user,
    update_user
)
from models.users import UserType, Status

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
    users = get_all_users()
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
    user = get_user_by_telegram_id(user_id)
    if user:
        return jsonify(user.to_dict())
    else:
        print(f"User with ID {user_id} not found")  # Debug statement
        return ('', 404)


@user_bp.route('/users/telegram/<int:telegram_id>', methods=['GET'])
@swag_from({
    'tags': ['Users'],
    'summary': 'Get a user by Telegram ID',
    'description': 'Retrieve a user by their Telegram ID.',
    'parameters': [
        {
            'name': 'telegram_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'The Telegram ID of the user'
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
def get_user_by_telegram_id_controller(telegram_id):
    # Use the service function to retrieve the user
    user = get_user_by_telegram_id(telegram_id)
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
    new_user = create_user(data)
    return jsonify(new_user.to_dict()), 201

@user_bp.route('/users/telegram/<int:telegram_id>', methods=['PUT'])
@swag_from({
    'tags': ['Users'],
    'summary': 'Update a user by Telegram ID',
    'description': 'Update an existing user by their Telegram ID with the provided data.',
    'parameters': [
        {
            'name': 'telegram_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'The Telegram ID of the user'
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
                    'telegram_id': {'type': 'integer'},
                    'status': {'type': 'string', 'enum': [e.value for e in Status]},
                    'type': {'type': 'string', 'enum': ['cliente']}
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
                    'telegram_id': {'type': 'integer'},
                    'status': {'type': 'string'},
                    'type': {'type': 'string'},
                    'creation_date': {'type': 'string', 'format': 'date-time'}
                }
            }
        },
        404: {
            'description': 'User not found'
        }
    }
})
def update_user_by_telegram_id(telegram_id):
    data = request.get_json()

    # Set default value for 'type' to 'cliente' if not provided
    data['type'] = data.get('type', 'cliente')
    data['status'] = data.get('status', 'activo')
    
    # Update the user using the service function to find by telegram_id
    user = get_user_by_telegram_id(telegram_id)
    if user:
        updated_user = update_user(user.id, data)
        return jsonify(updated_user.to_dict()) if updated_user else ('', 404)
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
    user = get_user_by_id(user_id)
    if user:
        db.session.delete(user)
        db.session.commit()
        return jsonify(user.to_dict())
    else:
        return ('', 404)
