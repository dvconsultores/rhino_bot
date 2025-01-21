# services/payment_service.py
from models.payment import Payment
from db import db  # Import db from db.py

def get_all_payments():
    return Payment.query.all()

def get_payments_by_year_and_month(year, month):
    """Retrieve payments by year and month."""
    payments = Payment.query.filter_by(year=year, month=month).all()
    return payments        

def get_payment_by_id(payment_id):
    return Payment.query.get(payment_id)

def create_payment(data):
    new_payment = Payment(**data)
    db.session.add(new_payment)
    db.session.commit()
    return new_payment

def update_payment(payment_id, data):
    payment = Payment.query.get(payment_id)
    if payment:
        for key, value in data.items():
            setattr(payment, key, value)
        db.session.commit()
    return payment

def delete_payment(payment_id):
    payment = Payment.query.get(payment_id)
    if payment:
        db.session.delete(payment)
        db.session.commit()
    return payment