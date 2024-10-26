# services/language_service.py
from models.language import Language
from db import db

def get_all_languages():
    return Language.query.all()

def get_language_by_telegram_id(id_telegram):
    return Language.query.filter_by(id_telegram=id_telegram).first()

def create_language(data):
    new_language = Language(**data)
    db.session.add(new_language)
    db.session.commit()
    return new_language

def update_language(id_telegram, data):
    language = Language.query.filter_by(id_telegram=id_telegram).first()
    if language:
        for key, value in data.items():
            setattr(language, key, value)
        db.session.commit()
    return language

def delete_language(id_telegram):
    language = Language.query.filter_by(id_telegram=id_telegram).first()
    if language:
        db.session.delete(language)
        db.session.commit()
    return language