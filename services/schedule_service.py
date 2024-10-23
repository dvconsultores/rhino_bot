# services/schedule_service.py
from models.schedule import Schedule
from db import db  # Import db from db.py

def get_all_schedules():
    return Schedule.query.all()

def get_schedule_by_id(schedule_id):
    return Schedule.query.get(schedule_id)

def create_schedule(data):
    new_schedule = Schedule(**data)
    db.session.add(new_schedule)
    db.session.commit()
    return new_schedule

def update_schedule(schedule_id, data):
    schedule = Schedule.query.get(schedule_id)
    if schedule:
        for key, value in data.items():
            setattr(schedule, key, value)
        db.session.commit()
    return schedule

def delete_schedule(schedule_id):
    schedule = Schedule.query.get(schedule_id)
    if schedule:
        db.session.delete(schedule)
        db.session.commit()
    return schedule