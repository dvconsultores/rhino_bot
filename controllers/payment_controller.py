# controllers/payment_controller.py
from flask import Blueprint, jsonify, request
from flasgger import swag_from
from models.payment import Payment
from db import db
from services.payment_service import get_all_payments, get_payment_by_id, create_payment, update_payment, delete_payment

payment_bp = Blueprint('payment_bp', __name__)

@payment_bp.route('/payments', methods=['GET'])
@swag_from({
    'tags': ['Payments'],
    'summary': 'Get all payments',
    'description': 'Retrieve a list of all payments.',
    'responses': {
        200: {
            'description': 'A list of payments',
            'schema': {
                'type': 'array',
                'items': {
                    'type': 'object',
                    'properties': {
                        'id': {'type': 'integer'},
                        'user_id': {'type': 'integer'},
                        'date': {'type': 'string', 'format': 'date'},
                        'amount': {'type': 'number'},
                        'reference': {'type': 'string'},
                        'payment_method_id': {'type': 'integer'},
                        'creation_date': {'type': 'string', 'format': 'date-time'},
                        'year': {'type': 'integer'},
                        'month': {'type': 'integer'}
                    }
                }
            }
        }
    }
})
def get_payments():
    payments = get_all_payments()
    return jsonify([payment.to_dict() for payment in payments])

@payment_bp.route('/payments/<int:payment_id>', methods=['GET'])
@swag_from({
    'tags': ['Payments'],
    'summary': 'Get a payment by ID',
    'description': 'Retrieve a payment by its ID.',
    'parameters': [
        {
            'name': 'payment_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'The ID of the payment'
        }
    ],
    'responses': {
        200: {
            'description': 'A payment',
            'schema': {
                'type': 'object',
                'properties': {
                    'id': {'type': 'integer'},
                    'user_id': {'type': 'integer'},
                    'date': {'type': 'string', 'format': 'date'},
                    'amount': {'type': 'number'},
                    'reference': {'type': 'string'},
                    'payment_method_id': {'type': 'integer'},
                    'creation_date': {'type': 'string', 'format': 'date-time'},
                    'year': {'type': 'integer'},
                    'month': {'type': 'integer'}
                }
            }
        },
        404: {
            'description': 'Payment not found'
        }
    }
})
def get_payment(payment_id):
    payment = get_payment_by_id(payment_id)
    return jsonify(payment.to_dict()) if payment else ('', 404)

@payment_bp.route('/payments', methods=['POST'])
@swag_from({
    'tags': ['Payments'],
    'summary': 'Add a new payment',
    'description': 'Create a new payment with the provided data.',
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'user_id': {'type': 'integer'},
                    'date': {'type': 'string', 'format': 'date'},
                    'amount': {'type': 'number'},
                    'reference': {'type': 'string'},
                    'payment_method_id': {'type': 'integer'},
                    'year': {'type': 'integer'},
                    'month': {'type': 'integer'}
                }
            }
        }
    ],
    'responses': {
        201: {
            'description': 'Payment created',
            'schema': {
                'type': 'object',
                'properties': {
                    'id': {'type': 'integer'},
                    'user_id': {'type': 'integer'},
                    'date': {'type': 'string', 'format': 'date'},
                    'amount': {'type': 'number'},
                    'reference': {'type': 'string'},
                    'payment_method_id': {'type': 'integer'},
                    'creation_date': {'type': 'string', 'format': 'date-time'},
                    'year': {'type': 'integer'},
                    'month': {'type': 'integer'}
                }
            }
        }
    }
})
def add_payment():
    data = request.get_json()
    new_payment = create_payment(data)
    return jsonify(new_payment.to_dict()), 201

@payment_bp.route('/payments/<int:payment_id>', methods=['PUT'])
@swag_from({
    'tags': ['Payments'],
    'summary': 'Edit a payment',
    'description': 'Update an existing payment with the provided data.',
    'parameters': [
        {
            'name': 'payment_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'The ID of the payment'
        },
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'user_id': {'type': 'integer'},
                    'date': {'type': 'string', 'format': 'date'},
                    'amount': {'type': 'number'},
                    'reference': {'type': 'string'},
                    'payment_method_id': {'type': 'integer'},
                    'year': {'type': 'integer'},
                    'month': {'type': 'integer'}
                }
            }
        }
    ],
    'responses': {
        200: {
            'description': 'Payment updated',
            'schema': {
                'type': 'object',
                'properties': {
                    'id': {'type': 'integer'},
                    'user_id': {'type': 'integer'},
                    'date': {'type': 'string', 'format': 'date'},
                    'amount': {'type': 'number'},
                    'reference': {'type': 'string'},
                    'payment_method_id': {'type': 'integer'},
                    'creation_date': {'type': 'string', 'format': 'date-time'},
                    'year': {'type': 'integer'},
                    'month': {'type': 'integer'}
                }
            }
        },
        404: {
            'description': 'Payment not found'
        }
    }
})
def edit_payment(payment_id):
    data = request.get_json()
    updated_payment = update_payment(payment_id, data)
    return jsonify(updated_payment.to_dict()) if updated_payment else ('', 404)

@payment_bp.route('/payments/<int:payment_id>', methods=['DELETE'])
@swag_from({
    'tags': ['Payments'],
    'summary': 'Delete a payment',
    'description': 'Delete an existing payment by its ID.',
    'parameters': [
        {
            'name': 'payment_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'The ID of the payment'
        }
    ],
    'responses': {
        204: {
            'description': 'Payment deleted'
        },
        404: {
            'description': 'Payment not found'
        }
    }
})
def remove_payment(payment_id):
    deleted_payment = delete_payment(payment_id)
    return '', 204 if deleted_payment else ('', 404)