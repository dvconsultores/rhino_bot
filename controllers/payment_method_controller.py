# controllers/payment_method_controller.py
from flask import Blueprint, jsonify, request
from flasgger import swag_from
from models.payment_methods import PaymentMethods
from db import db

payment_method_bp = Blueprint('payment_method_bp', __name__)

@payment_method_bp.route('/payment_methods', methods=['GET'])
@swag_from({
    'tags': ['Payment Methods'],
    'summary': 'Get all payment methods',
    'description': 'Retrieve a list of all payment methods.',
    'responses': {
        200: {
            'description': 'A list of payment methods',
            'schema': {
                'type': 'array',
                'items': {
                    'type': 'object',
                    'properties': {
                        'id': {'type': 'integer'},
                        'method': {'type': 'string'},
                        'creation_date': {'type': 'string', 'format': 'date-time'}
                    }
                }
            }
        }
    }
})
def get_payment_methods():
    payment_methods = PaymentMethods.query.all()
    return jsonify([payment_method.to_dict() for payment_method in payment_methods])

@payment_method_bp.route('/payment_methods/<int:payment_method_id>', methods=['GET'])
@swag_from({
    'tags': ['Payment Methods'],
    'summary': 'Get a payment method by ID',
    'description': 'Retrieve a payment method by its ID.',
    'parameters': [
        {
            'name': 'payment_method_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'The ID of the payment method'
        }
    ],
    'responses': {
        200: {
            'description': 'A payment method',
            'schema': {
                'type': 'object',
                'properties': {
                    'id': {'type': 'integer'},
                    'method': {'type': 'string'},
                    'creation_date': {'type': 'string', 'format': 'date-time'}
                }
            }
        },
        404: {
            'description': 'Payment method not found'
        }
    }
})
def get_payment_method(payment_method_id):
    payment_method = PaymentMethods.query.get(payment_method_id)
    return jsonify(payment_method.to_dict()) if payment_method else ('', 404)

@payment_method_bp.route('/payment_methods', methods=['POST'])
@swag_from({
    'tags': ['Payment Methods'],
    'summary': 'Add a new payment method',
    'description': 'Create a new payment method with the provided data.',
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'method': {'type': 'string'}
                }
            }
        }
    ],
    'responses': {
        201: {
            'description': 'Payment method created',
            'schema': {
                'type': 'object',
                'properties': {
                    'id': {'type': 'integer'},
                    'method': {'type': 'string'},
                    'creation_date': {'type': 'string', 'format': 'date-time'}
                }
            }
        }
    }
})
def add_payment_method():
    data = request.get_json()
    new_payment_method = PaymentMethods(method=data['method'])
    db.session.add(new_payment_method)
    db.session.commit()
    return jsonify(new_payment_method.to_dict()), 201

@payment_method_bp.route('/payment_methods/<int:payment_method_id>', methods=['PUT'])
@swag_from({
    'tags': ['Payment Methods'],
    'summary': 'Edit a payment method',
    'description': 'Update an existing payment method with the provided data.',
    'parameters': [
        {
            'name': 'payment_method_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'The ID of the payment method'
        },
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'method': {'type': 'string'}
                }
            }
        }
    ],
    'responses': {
        200: {
            'description': 'Payment method updated',
            'schema': {
                'type': 'object',
                'properties': {
                    'id': {'type': 'integer'},
                    'method': {'type': 'string'},
                    'creation_date': {'type': 'string', 'format': 'date-time'}
                }
            }
        },
        404: {
            'description': 'Payment method not found'
        }
    }
})
def edit_payment_method(payment_method_id):
    data = request.get_json()
    payment_method = PaymentMethods.query.get(payment_method_id)
    if payment_method:
        payment_method.method = data['method']
        db.session.commit()
        return jsonify(payment_method.to_dict())
    else:
        return '', 404

@payment_method_bp.route('/payment_methods/<int:payment_method_id>', methods=['DELETE'])
@swag_from({
    'tags': ['Payment Methods'],
    'summary': 'Delete a payment method',
    'description': 'Delete an existing payment method by its ID.',
    'parameters': [
        {
            'name': 'payment_method_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'The ID of the payment method'
        }
    ],
    'responses': {
        204: {
            'description': 'Payment method deleted'
        },
        404: {
            'description': 'Payment method not found'
        }
    }
})
def delete_payment_method(payment_method_id):
    payment_method = PaymentMethods.query.get(payment_method_id)
    if payment_method:
        db.session.delete(payment_method)
        db.session.commit()
        return '', 204
    else:
        return '', 404