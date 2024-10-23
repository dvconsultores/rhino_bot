# controllers/schedule_controller.py
from flask import Blueprint, request, jsonify
from services.schedule_service import get_all_schedules, get_schedule_by_id, create_schedule, update_schedule, delete_schedule

schedule_bp = Blueprint('schedule', __name__)

@schedule_bp.route('/schedules', methods=['GET'])
def get_schedules():
    schedules = get_all_schedules()
    return jsonify([schedule.__dict__ for schedule in schedules])

@schedule_bp.route('/schedules/<int:schedule_id>', methods=['GET'])
def get_schedule(schedule_id):
    schedule = get_schedule_by_id(schedule_id)
    return jsonify(schedule.__dict__) if schedule else ('', 404)

@schedule_bp.route('/schedules', methods=['POST'])
def add_schedule():
    data = request.get_json()
    new_schedule = create_schedule(data)
    return jsonify(new_schedule.__dict__), 201

@schedule_bp.route('/schedules/<int:schedule_id>', methods=['PUT'])
def edit_schedule(schedule_id):
    data = request.get_json()
    updated_schedule = update_schedule(schedule_id, data)
    return jsonify(updated_schedule.__dict__) if updated_schedule else ('', 404)

@schedule_bp.route('/schedules/<int:schedule_id>', methods=['DELETE'])
def remove_schedule(schedule_id):
    deleted_schedule = delete_schedule(schedule_id)
    return jsonify(deleted_schedule.__dict__) if deleted_schedule else ('', 404)