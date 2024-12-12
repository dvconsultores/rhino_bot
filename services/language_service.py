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
    """
    Update the language of a user identified by `id_telegram`.
    
    :param id_telegram: The Telegram ID of the user.
    :param data: A dictionary containing the fields to update.
    :return: The updated Language object or None if not found.
    """
    # Find the language entry by Telegram ID
    language = Language.query.filter_by(id_telegram=id_telegram).first()
    if language:
        # Ensure the key 'language' in the input maps to 'Language' in the model
        for key, value in data.items():
            if key.lower() == 'language' and hasattr(language, 'Language'):
                setattr(language, 'Language', value)
            else:
                print(f"Key '{key}' is not recognized or does not exist in the Language model.")
        
        # Commit changes to the database
        db.session.commit()
        print("Updated Language:", language.to_dict())
    else:
        print(f"No language found with id_telegram: {id_telegram}")

    return language


def delete_language(id_telegram):
    language = Language.query.filter_by(id_telegram=id_telegram).first()
    if language:
        db.session.delete(language)
        db.session.commit()
    return language