from models.schedule import Schedule
from db import db  # Import db from db.py
from sqlalchemy.orm import joinedload

def get_all_schedules():
    """
    Get all schedules from the database.
    """
    return Schedule.query.all()

def get_schedule_by_id(schedule_id):
    """
    Get a specific schedule by its ID.
    """
    return Schedule.query.get(schedule_id)

def create_schedule(data):
    """
    Create a new schedule in the database.
    The data should be a dictionary containing location_id, days, time_init, and creation_date.
    """
    # Ensure that 'days' is passed as a string, as the model now expects a string for 'days'
    if isinstance(data.get('days'), list):
        data['days'] = ', '.join(data['days'])  # Convert list of days to a comma-separated string

    new_schedule = Schedule(**data)
    db.session.add(new_schedule)
    db.session.commit()
    return new_schedule

def update_schedule(schedule_id, data):
    """
    Update an existing schedule in the database based on its ID.
    """
    schedule = Schedule.query.get(schedule_id)
    if schedule:
        for key, value in data.items():
            setattr(schedule, key, value)
        db.session.commit()
    return schedule

def delete_schedule(schedule_id):
    schedule = Schedule.query.options(joinedload(Schedule.location)).get(schedule_id)
    if schedule:
        db.session.delete(schedule)
        db.session.commit()
    return schedule
