# services/payment_method_service.py
from models.payment_methods import PaymentMethods
from db import db  # Import db from db.py

def get_all_payment_methods():
    return PaymentMethods.query.all()

def get_payment_method_by_id(payment_method_id):
    return PaymentMethods.query.get(payment_method_id)

def create_payment_method(data):
    new_payment_method = PaymentMethods(**data)
    db.session.add(new_payment_method)
    db.session.commit()
    return new_payment_method

def update_payment_method(payment_method_id, data):
    payment_method = PaymentMethods.query.get(payment_method_id)
    if payment_method:
        for key, value in data.items():
            setattr(payment_method, key, value)
        db.session.commit()
    return payment_method

def delete_payment_method(payment_method_id):
    payment_method = PaymentMethods.query.get(payment_method_id)
    if payment_method:
        db.session.delete(payment_method)
        db.session.commit()
    return payment_method