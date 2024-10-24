# services/language_service.py
from models.language import Language
from db import db

def get_all_languages():
    return Language.query.all()

def get_language_by_id(language_id):
    return Language.query.get(language_id)

def create_language(data):
    new_language = Language(**data)
    db.session.add(new_language)
    db.session.commit()
    return new_language

def update_language(language_id, data):
    language = Language.query.get(language_id)
    if language:
        for key, value in data.items():
            setattr(language, key, value)
        db.session.commit()
    return language

def delete_language(language_id):
    language = Language.query.get(language_id)
    if language:
        db.session.delete(language)
        db.session.commit()
    return language