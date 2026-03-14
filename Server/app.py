from flask import Flask, request, jsonify
from datetime import datetime
from functools import wraps
import logging
import os
import dotenv

app = Flask(__name__)
token = ''

def verification_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        payload_token = request.form.get('token')
        if token != payload_token:
            return jsonify({
                'message': 'verification_failed'
            }), 401
        func(*args, **kwargs)
    return wrapper

@app.route('/api/update')
@verification_required
def update():
    pass

@app.route('/api/spy')
def spy():
    pass

if __name__ == '__main__':
    dotenv.load_dotenv()
    token = os.getenv('TOKEN')
    app.run()
    