from models.coaches import Coach
from sqlalchemy.orm import joinedload
from db import db

class CoachesService:
    @staticmethod
    def create_coach(cedula, names, location_id):
        """Create a new coach."""
        new_coach = Coach(cedula=cedula, names=names, location_id=location_id)
        db.session.add(new_coach)
        db.session.commit()
        return new_coach

    @staticmethod
    def get_coach_by_id(coach_id, eager_load=False):
        query = db.session.query(Coach)
        if eager_load:
            query = query.options(joinedload(Coach.location))  # Eagerly load `location`
        return query.filter(Coach.id == coach_id).first()

    @staticmethod
    def get_all_coaches():
        """Retrieve all coaches."""
        return Coach.query.all()

    @staticmethod
    def update_coach(coach_id, cedula=None, names=None, location_id=None):
        """Update an existing coach."""
        coach = Coach.query.get(coach_id)
        if coach:
            if cedula:
                coach.cedula = cedula
            if names:
                coach.names = names
            if location_id:
                coach.location_id = location_id
            db.session.commit()
        return coach

    @staticmethod
    def delete_coach(coach_id):
        """Delete a coach by ID."""
        coach = Coach.query.get(coach_id)
        if coach:
            db.session.delete(coach)
            db.session.commit()
        return coach