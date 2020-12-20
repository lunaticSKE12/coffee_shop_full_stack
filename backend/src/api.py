import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)


db_drop_and_create_all()

# ROUTES


@app.route('/drinks', methods=['GET'])
def get_drinks():
    drinks = Drink.query.all()
    drinks = [drink.short() for drink in drinks]

    return jsonify({
        'success': True,
        'drinks': drinks
    }), 200


@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def get_drinks_details(token):
    drinks = Drink.query.all()
    drinks = [drink.long() for drink in drinks]

    return jsonify({
        'success': True,
        'drinks': drinks
    }), 200


@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def post_drinks(payload):
    body = request.get_json()

    try:
        title = body['title']
        recipe = json.dumps(body['recipe'])

        drink = Drink(title=title, recipe=recipe)
        drink.insert()
        return jsonify({
            'success': True,
            'drink': drink.long()
        }), 200
    except:
        abort(422)


@app.route('/drinks/<id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drink(payload, id):
    drink = Drink.query.get(id)
    if drink is None:
        return json.dumps({
            'success':
            False,
            'error':
            'Drink #' + id + ' not found to be edited'
        }), 404

    body = request.get_json()
    title = body['title']
    recipe = body['recipe']

    if title:
        drink.title = title
    if recipe:
        drink.recipe = json.dumps(recipe)
    drink.update()

    return jsonify({
        'success': True,
        'drinks': drink.long()
    }), 200


@app.route('/drinks/<int:id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drinks(id):
    drinks = Drink.query.get(id)
    if not drinks:
        abort(404)

    drinks.delete()

    return jsonify({
        'success': True,
        'delete': id
    }), 200


# Error Handling

@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


@app.errorhandler(401)
def unauthorized(error):
    return jsonify({
        'success': False,
        'error': 401,
        'message': "unauthorized"
    }), 401


@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 404,
        'message': 'not found'
    }), 404


@app.errorhandler(AuthError)
def auth_error(error):
    return jsonify({
        'success': False,
        'error': error.status_code,
        'message': error.error['description']
    }), error.status_code
