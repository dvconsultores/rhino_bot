# models/payment.py
from db import db  # Import db from db.py
from models.users import User
from models.payment_methods import PaymentMethods
from datetime import datetime
from collections import OrderedDict

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

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'date': self.date.isoformat(),
            'amount': self.amount,
            'reference': self.reference,
            'payment_method_id': self.payment_method_id,
            'creation_date': self.creation_date.isoformat(),
            'year': self.year,
                'month': self.month
            }

    def to_custom_dict(self):
        return OrderedDict([
            ('Usuario', f"{self.user.name} {self.user.lastname}"),
            ('FechaCreación', self.creation_date.isoformat()),
            ('Fecha', self.date.isoformat()),
            ('MétodoPago', self.payment_method.method),
            ('Referencia', self.reference),
            ('Monto', self.amount),
            ('Año', self.year),
            ('Mes', self.month),
            ('ImageRef', f"{self.user.telegram_id}_{self.date.strftime('%Y%m%d')}")
        ])     

    def __repr__(self):
        fields = ', '.join(f'{key}={value}' for key, value in self.__dict__.items() if not key.startswith('_'))
        return f'<Payment {fields}>'