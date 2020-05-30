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

'''
@TODO uncomment the following line to initialize the database
# Done
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
db_drop_and_create_all()

## ROUTES


'''
@TODO implement endpoint
# Done
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks', methods=['GET'])
def get_drinks():
    drinks = list(map(Drink.short, Drink.query.all()))
    return jsonify({"success": True,
                    "drinks": drinks}), 200


'''
@TODO implement endpoint
# Done
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def get_drinks_detail():
    try:
        drinks_details = list(map(Drink.long, Drink.query.all()))

        return jsonify({"success": True,
                        "drinks": drinks_details}), 200
    except Exception:
        abort(404)


'''
@TODO implement endpoint
# Done
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def add_drink():
    try:
        request_body = request.get_json(force=True)
        title = request_body.get('title', None)
        recipe = request_body.get('recipe', None)
        drink = Drink(title=title, recipe=json.dumps(recipe))
        Drink.insert(drink)

        new_drink = Drink.query.filter_by(id=drink.id).first()

        return jsonify({
            'success': True,
            'drinks': list(new_drink.long())
        }), 200
    except Exception:
        abort(422)


'''
@TODO implement endpoint
# Done
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks/<int:drink_id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def replace_drink(drink_id):
    request_body = request.get_json()
    new_title = request_body.get('title', None)
    new_recipe = request_body.get('recipe', None)

    try:
        drink = Drink.query.filter(Drink.id == drink_id).one_or_none()

        if drink is None:
            abort(404)
        if new_title is None:
            abort(400)
        if new_title is not None:
            drink.title = new_title
        if new_recipe is not None:
            drink.recipe = json.dumps(new_recipe)

        drink.update()
        updated_drink = drink.query.filter_by(drink.id == drink_id).first()

        return jsonify({"success": True,
                        "drinks": list(updated_drink.long)}), 200

    except Exception:
        abort(401)


'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks/<int:drink_id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(drink_id):
    try:
        drink = Drink.query.filter(Drink.id == drink_id).one_or_none()

        if drink is None:
            abort(404)

        drink.delete()
        return jsonify({
            "success": True,
            "delete": drink_id}), 200

    except Exception:
        abort(422)


## Error Handling
'''
Example error handling for unprocessable entity
'''


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False, 
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''


@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404


'''
@TODO implement error handler for AuthError
    error handler should conform to general task above 
'''


@app.errorhandler(AuthError)
def auth_error(error):
    return jsonify({'success': False,
                    'error': error.status_code,
                    'message': error.error['description']
                    }), error.status_code
