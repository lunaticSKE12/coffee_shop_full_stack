import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
# CORS(app)
CORS(app, resources={'/': {'origins': '*'}})


@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Headers',
                         'Content-Type,Authorization,true')
    response.headers.add('Access-Control-Allow-Methods',
                         'GET,PUT,POST,DELETE,OPTIONS')
    return response


db_drop_and_create_all()

# ROUTES


@app.route('/')
def handler():
    return jsonify({
        "success": True
    })


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
def get_drinks_detail(payload):
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
    title = body.get('title', None)
    recipe = str(json.dumps(data.get('recipe', None)))

    drink = Drink(title=title, recipe=recipe)
    drink.insert()
    return jsonify({
        'success': True,
        'drink': drink.long()
    }), 200


@app.route('/drinks/<int:id>', methods='PATCH')
@requires_auth('patch:drinks')
def update_drinks(id):
    drink = Drink.query.get(id)
    if not drink:
        abort(404)

    body = request.get_json()
    title = body.get('title', None)
    recipe = str(json.dumps(data.get('recipe', None)))

    if title is not None:
        drink.title = title
    if recipe is not None:
        drink.recipe = recipe
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
