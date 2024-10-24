# controllers/plan_controller.py
from flask import Blueprint, request, jsonify
from services.plan_service import get_all_plans, get_plan_by_id, create_plan, update_plan, delete_plan

plan_bp = Blueprint('plan', __name__)

@plan_bp.route('/plans', methods=['GET'])
def get_plans():
    plans = get_all_plans()
    return jsonify([plan.__dict__ for plan in plans])

@plan_bp.route('/plans/<int:plan_id>', methods=['GET'])
def get_plan(plan_id):
    plan = get_plan_by_id(plan_id)
    return jsonify(plan.__dict__) if plan else ('', 404)

@plan_bp.route('/plans', methods=['POST'])
def add_plan():
    data = request.get_json()
    new_plan = create_plan(data)
    return jsonify(new_plan.__dict__), 201

@plan_bp.route('/plans/<int:plan_id>', methods=['PUT'])
def edit_plan(plan_id):
    data = request.get_json()
    updated_plan = update_plan(plan_id, data)
    return jsonify(updated_plan.__dict__) if updated_plan else ('', 404)

@plan_bp.route('/plans/<int:plan_id>', methods=['DELETE'])
def remove_plan(plan_id):
    deleted_plan = delete_plan(plan_id)
    return jsonify(deleted_plan.__dict__) if deleted_plan else ('', 404)