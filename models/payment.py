# models/payment.py
from db import db  # Import db from db.py
from models.users import User
from models.payment_methods import PaymentMethods
from datetime import datetime

class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    amount = db.Column(db.Float, nullable=False)
    reference = db.Column(db.String(120), nullable=False)
    payment_method_id = db.Column(db.Integer, db.ForeignKey('payment_methods.id'), nullable=False)
    creation_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    year = db.Column(db.Integer, nullable=False)
    month = db.Column(db.Integer, nullable=False)

    user = db.relationship('User', backref=db.backref('payments', lazy=True))
    payment_method = db.relationship('PaymentMethods', backref=db.backref('payments', lazy=True))

    def __repr__(self):
        fields = ', '.join(f'{key}={value}' for key, value in self.__dict__.items() if not key.startswith('_'))
        return f'<Payment {fields}>'