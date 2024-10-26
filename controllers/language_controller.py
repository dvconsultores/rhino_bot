# controllers/language_controller.py
from flask import Blueprint, request, jsonify
from flasgger import swag_from
from services.language_service import get_all_languages, get_language_by_telegram_id, create_language, update_language

language_bp = Blueprint('language', __name__)

@language_bp.route('/languages', methods=['GET'])
@swag_from({
    'tags': ['Languages'],
    'responses': {
        200: {
            'description': 'A list of languages',
            'schema': {
                'type': 'array',
                'items': {
                    'type': 'object',
                    'properties': {
                        'id': {'type': 'integer'},
                        'id_telegram': {'type': 'integer'},
                        'Language': {'type': 'string'},
                        'creation_date': {'type': 'string', 'format': 'date-time'}
                    }
                }
            }
        }
    }
})
def get_languages():
    languages = get_all_languages()
    return jsonify([language.to_dict() for language in languages])

@language_bp.route('/languages/<int:id_telegram>', methods=['GET'])
@swag_from({
    'tags': ['Languages'],
    'summary': 'Get a language by Telegram ID',
    'description': 'Retrieve a language by its Telegram ID.',
    'parameters': [
        {
            'name': 'id_telegram',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'The Telegram ID of the language'
        }
    ],
    'responses': {
        200: {
            'description': 'A language',
            'schema': {
                'type': 'object',
                'properties': {
                    'id': {'type': 'integer'},
                    'id_telegram': {'type': 'integer'},
                    'Language': {'type': 'string'},
                    'creation_date': {'type': 'string', 'format': 'date-time'}
                }
            }
        },
        404: {
            'description': 'Language not found'
        }
    }
})
def get_language(id_telegram):
    language = get_language_by_telegram_id(id_telegram)
    return jsonify(language.to_dict()) if language else ('', 404)

@language_bp.route('/languages', methods=['POST'])
@swag_from({
    'tags': ['Languages'],
    'summary': 'Create a new language',
    'description': 'Create a new language with the provided data.',
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'id_telegram': {'type': 'integer'},
                    'Language': {'type': 'string'}
                }
            }
        }
    ],
    'responses': {
        201: {
            'description': 'Language created',
            'schema': {
                'type': 'object',
                'properties': {
                    'id': {'type': 'integer'},
                    'id_telegram': {'type': 'integer'},
                    'Language': {'type': 'string'},
                    'creation_date': {'type': 'string', 'format': 'date-time'}
                }
            }
        }
    }
})
def create_language():
    data = request.get_json()
    new_language = create_language(data)
    return jsonify(new_language.to_dict()), 201

@language_bp.route('/languages/<int:id_telegram>', methods=['PUT'])
@swag_from({
    'tags': ['Languages'],
    'summary': 'Update a language',
    'description': 'Update an existing language with the provided data.',
    'parameters': [
        {
            'name': 'id_telegram',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'The Telegram ID of the language'
        },
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'id_telegram': {'type': 'integer'},
                    'Language': {'type': 'string'}
                }
            }
        }
    ],
    'responses': {
        200: {
            'description': 'Language updated',
            'schema': {
                'type': 'object',
                'properties': {
                    'id': {'type': 'integer'},
                    'id_telegram': {'type': 'integer'},
                    'Language': {'type': 'string'},
                    'creation_date': {'type': 'string', 'format': 'date-time'}
                }
            }
        },
        404: {
            'description': 'Language not found'
        }
    }
})
def update_language_controller(id_telegram):
    data = request.get_json()
    updated_language = update_language(id_telegram, data)
    return jsonify(updated_language.to_dict()) if updated_language else ('', 404)

@language_bp.route('/languages/<int:id_telegram>', methods=['DELETE'])
@swag_from({
    'tags': ['Languages'],
    'summary': 'Delete a language',
    'description': 'Delete a language by its Telegram ID.',
    'parameters': [
        {
            'name': 'id_telegram',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'The Telegram ID of the language'
        }
    ],
    'responses': {
        200: {
            'description': 'Language deleted',
            'schema': {
                'type': 'object',
                'properties': {
                    'id': {'type': 'integer'},
                    'id_telegram': {'type': 'integer'},
                    'Language': {'type': 'string'},
                    'creation_date': {'type': 'string', 'format': 'date-time'}
                }
            }
        },
        404: {
            'description': 'Language not found'
        }
    }
})
def delete_language(id_telegram):
    deleted_language = delete_language(id_telegram)
    return jsonify(deleted_language.to_dict()) if deleted_language else ('', 404)