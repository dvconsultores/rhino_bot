# controllers/payment_method_controller.py
from flask import Blueprint, request, jsonify
from services.payment_method_service import get_all_payment_methods, get_payment_method_by_id, create_payment_method, update_payment_method, delete_payment_method

payment_method_bp = Blueprint('payment_method', __name__)

@payment_method_bp.route('/payment_methods', methods=['GET'])
def get_payment_methods():
    payment_methods = get_all_payment_methods()
    return jsonify([payment_method.__dict__ for payment_method in payment_methods])

@payment_method_bp.route('/payment_methods/<int:payment_method_id>', methods=['GET'])
def get_payment_method(payment_method_id):
    payment_method = get_payment_method_by_id(payment_method_id)
    return jsonify(payment_method.__dict__) if payment_method else ('', 404)

@payment_method_bp.route('/payment_methods', methods=['POST'])
def add_payment_method():
    data = request.get_json()
    new_payment_method = create_payment_method(data)
    return jsonify(new_payment_method.__dict__), 201

@payment_method_bp.route('/payment_methods/<int:payment_method_id>', methods=['PUT'])
def edit_payment_method(payment_method_id):
    data = request.get_json()
    updated_payment_method = update_payment_method(payment_method_id, data)
    return jsonify(updated_payment_method.__dict__) if updated_payment_method else ('', 404)

@payment_method_bp.route('/payment_methods/<int:payment_method_id>', methods=['DELETE'])
def remove_payment_method(payment_method_id):
    deleted_payment_method = delete_payment_method(payment_method_id)
    return jsonify(deleted_payment_method.__dict__) if deleted_payment_method else ('', 404)