# controllers/language_controller.py
from flask import Blueprint, request, jsonify
from flasgger import swag_from
from models.language import Language

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
    'parameters': [
        {
            'name': 'id_telegram',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'The Telegram ID of the language'
        }
    ],
    'tags': ['Languages'],
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
    'tags': ['Languages'],
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
def add_language():
    data = request.get_json()
    new_language = create_language(data)
    return jsonify(new_language.to_dict()), 201

@language_bp.route('/languages/<int:id_telegram>', methods=['PUT'])
@swag_from({
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
    'tags': ['Languages'], 
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
def edit_language(id_telegram):
    data = request.get_json()
    updated_language = update_language(id_telegram, data)
    return jsonify(updated_language.to_dict()) if updated_language else ('', 404)