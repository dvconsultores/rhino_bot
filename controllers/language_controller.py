# controllers/language_controller.py
from flask import Blueprint, request, jsonify
from services.language_service import get_all_languages, get_language_by_id, create_language, update_language, delete_language

language_bp = Blueprint('language', __name__)

@language_bp.route('/languages', methods=['GET'])
def get_languages():
    languages = get_all_languages()
    return jsonify([language.__dict__ for language in languages])

@language_bp.route('/languages/<int:language_id>', methods=['GET'])
def get_language(language_id):
    language = get_language_by_id(language_id)
    return jsonify(language.__dict__) if language else ('', 404)

@language_bp.route('/languages', methods=['POST'])
def add_language():
    data = request.get_json()
    new_language = create_language(data)
    return jsonify(new_language.__dict__), 201

@language_bp.route('/languages/<int:language_id>', methods=['PUT'])
def edit_language(language_id):
    data = request.get_json()
    updated_language = update_language(language_id, data)
    return jsonify(updated_language.__dict__) if updated_language else ('', 404)

@language_bp.route('/languages/<int:language_id>', methods=['DELETE'])
def remove_language(language_id):
    deleted_language = delete_language(language_id)
    return jsonify(deleted_language.__dict__) if deleted_language else ('', 404)