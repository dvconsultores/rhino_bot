from db import db  # Import db from db.py
from models.users import User
from models.coaches import Coach
from models.locations import Locations
from datetime import datetime

class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    coach_id = db.Column(db.Integer, db.ForeignKey('coach.id'), nullable=False)
    location_id = db.Column(db.Integer, db.ForeignKey('locations.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    creation_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    coach = db.relationship('Coach', backref=db.backref('attendances', lazy=True))  # String reference
    location = db.relationship('Locations', backref=db.backref('attendances', lazy=True))  # String reference
    user = db.relationship('User', backref=db.backref('attendances', lazy=True))  # String reference

    def to_dict(self):
        return {
            'id': self.id,
            'coach_id': self.coach_id,
            'coach_name': self.coach.names if self.coach else None,
            'location_id': self.location_id,
            'location_name': self.location.location if self.location else None,
            'user_id': self.user_id,
            'user_name': self.user.name if self.user else None,
            'date': self.date.isoformat(),
            'creation_date': self.creation_date.isoformat()
        }

    def __repr__(self):
        return f"<Attendance id={self.id}, coach_id={self.coach_id}, location_id={self.location_id}, user_id={self.user_id}, date={self.date}>"