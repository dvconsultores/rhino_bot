from flask import Blueprint, jsonify, request
from flasgger import swag_from
from models.plans import Plans
from db import db

plan_bp = Blueprint('plan', __name__)

@plan_bp.route('/plans', methods=['GET'])
@swag_from({
    'tags': ['Plans'],
    'responses': {
        200: {
            'description': 'List all plans',
            'schema': {
                'type': 'array',
                'items': {
                    'type': 'object',
                    'properties': {
                        'id': {'type': 'integer'},
                        'name': {'type': 'string'},
                        'price': {'type': 'number'}
                    }
                }
            }
        }
    }
})
def get_plans():
    plans = Plans.query.all()
    return jsonify([plan.to_dict() for plan in plans])

@plan_bp.route('/plans', methods=['POST'])
@swag_from({
    'tags': ['Plans'],
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'schema': {
                'type': 'object',
                'properties': {
                    'name': {'type': 'string'},
                    'price': {'type': 'number'}
                },
                'required': ['name', 'price']
            }
        }
    ],
    'responses': {
        201: {
            'description': 'Plan created successfully',
            'schema': {
                'type': 'object',
                'properties': {
                    'id': {'type': 'integer'},
                    'name': {'type': 'string'},
                    'price': {'type': 'number'}
                }
            }
        }
    }
})
def create_plan():
    data = request.get_json()
    if not data or 'name' not in data or 'price' not in data:
        return jsonify({"error": "Invalid input"}), 400

    new_plan = Plans(name=data['name'], price=data['price'])
    db.session.add(new_plan)
    db.session.commit()
    return jsonify(new_plan.to_dict()), 201

@plan_bp.route('/plans/<int:plan_id>', methods=['PUT'])
@swag_from({
    'tags': ['Plans'],
    'parameters': [
        {
            'name': 'plan_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'ID of the plan to update'
        },
        {
            'name': 'body',
            'in': 'body',
            'schema': {
                'type': 'object',
                'properties': {
                    'name': {'type': 'string'},
                    'price': {'type': 'number'}
                },
                'required': ['name', 'price']
            }
        }
    ],
    'responses': {
        200: {
            'description': 'Plan updated successfully',
            'schema': {
                'type': 'object',
                'properties': {
                    'id': {'type': 'integer'},
                    'name': {'type': 'string'},
                    'price': {'type': 'number'}
                }
            }
        },
        404: {'description': 'Plan not found'}
    }
})
def edit_plan(plan_id):
    data = request.get_json()
    updated_plan = update_plan(plan_id, data)
    return jsonify(updated_plan.to_dict()) if updated_plan else ('', 404)

def update_plan(plan_id, data):
    plan = Plans.query.get(plan_id)
    if plan:
        plan.name = data['name']
        plan.price = data['price']
        db.session.commit()
        return plan
    return None

@plan_bp.route('/plans/<int:plan_id>', methods=['DELETE'])
@swag_from({
    'tags': ['Plans'],
    'parameters': [
        {
            'name': 'plan_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'ID of the plan to delete'
        }
    ],
    'responses': {
        200: {'description': 'Plan deleted successfully'},
        404: {'description': 'Plan not found'}
    }
})
def remove_plan(plan_id):
    """Remove a plan
    ---
    tags:
      - Plans
    """
    deleted_plan = delete_plan(plan_id)
    return jsonify(deleted_plan.to_dict()) if deleted_plan else ('', 404)

def delete_plan(plan_id):
    plan = Plans.query.get(plan_id)
    if plan:
        db.session.delete(plan)
        db.session.commit()
        return plan
    return None
