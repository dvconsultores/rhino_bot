# services/plan_service.py
from models.plans import Plans
from db import db  # Import db from db.py

def get_all_plans():
    return Plans.query.all()

def get_plan_by_id(plan_id):
    return Plans.query.get(plan_id)

def create_plan(data):
    new_plan = Plans(**data)
    db.session.add(new_plan)
    db.session.commit()
    return new_plan

def update_plan(plan_id, data):
    plan = Plans.query.get(plan_id)
    if plan:
        for key, value in data.items():
            setattr(plan, key, value)
        db.session.commit()
    return plan

def delete_plan(plan_id):
    plan = Plans.query.get(plan_id)
    if plan:
        db.session.delete(plan)
        db.session.commit()
    return plan