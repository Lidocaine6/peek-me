from flask import Flask, request, jsonify
from datetime import datetime
from functools import wraps
import logging
import os
import dotenv

app = Flask(__name__)
token = ''

device_format_string = """
设备：{device_name}
- 正在使用的程序：{program_name}{extra_data}
- 更新时间：{time}
""".strip()

class Device:
    def __init__(self, device_name: str, online: bool=True):
        self.device_name = device_name
        self.online = online
        self.program_name = ''
        self.extra_data = ''
        self.time_last_updated = datetime.now()

    def update(self, program_name: str, extra_data: str=''):
        self.time_last_updated = datetime.now()
        self.program_name = program_name
        self.extra_data = extra_data
    
    def to_string(self):
        return device_format_string.format(
            device_name=self.device_name,
            program_name=self.program_name,
            extra_data='\n- ' + self.extra_data if self.extra_data != '' else '',
            time=self.time_last_updated.strftime('%Y/%m/%d/ %H:%M:%S')
        )

    def switch_online_state(self, state: bool=None):
        self.time_last_updated = datetime.now()
        if state:
            self.online = not self.online
        else:
            self.online = state

device_list = {
    'Windows': Device('💻电脑'),
    'Android': Device('📱手机'),
}

def verification_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        payload_token = request.form.get('token')
        if token != payload_token:
            return jsonify({
                'error': 'Verification failed'
            }), 401
        func(*args, **kwargs)
    return wrapper

def required_params(*params):
    def wrapper(f):
        @wraps(f)
        def decorated_func(*args, **kwargs):
            missing = [param for param in params if param not in request.form]
            if missing:
                return jsonify({
                    'error': 'Invalid argument',
                }), 400
            return f(*args, **kwargs)
        return decorated_func
    return wrapper

@app.route('/api/update')
@verification_required
@required_params('device_name', 'program_name')
def update():
    device_name = request.form['device_name']
    program_name = request.form['program_name']
    extra_data = request.form['extra_data']
    if not (device_name in device_list):
        return jsonify({
            'error': 'Invalid device name'
        }), 400
    device_list[device_name].update(program_name, extra_data)
    

@app.route('/api/spy')
@verification_required
def spy():
    response = ''
    for device in device_list:
        response += device_list[device].to_string()
        response += '\n'
    response.strip()
    return response


if __name__ == '__main__':
    dotenv.load_dotenv()
    token = os.getenv('TOKEN')
    app.run()
    