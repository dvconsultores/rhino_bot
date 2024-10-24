# controllers/payment_controller.py
from flask import Blueprint, request, jsonify
from services.payment_service import get_all_payments, get_payment_by_id, create_payment, update_payment, delete_payment

payment_bp = Blueprint('payment', __name__)

@payment_bp.route('/payments', methods=['GET'])
def get_payments():
    payments = get_all_payments()
    return jsonify([payment.__dict__ for payment in payments])

@payment_bp.route('/payments/<int:payment_id>', methods=['GET'])
def get_payment(payment_id):
    payment = get_payment_by_id(payment_id)
    return jsonify(payment.__dict__) if payment else ('', 404)

@payment_bp.route('/payments', methods=['POST'])
def add_payment():
    data = request.get_json()
    new_payment = create_payment(data)
    return jsonify(new_payment.__dict__), 201

@payment_bp.route('/payments/<int:payment_id>', methods=['PUT'])
def edit_payment(payment_id):
    data = request.get_json()
    updated_payment = update_payment(payment_id, data)
    return jsonify(updated_payment.__dict__) if updated_payment else ('', 404)

@payment_bp.route('/payments/<int:payment_id>', methods=['DELETE'])
def remove_payment(payment_id):
    deleted_payment = delete_payment(payment_id)
    return jsonify(deleted_payment.__dict__) if deleted_payment else ('', 404)