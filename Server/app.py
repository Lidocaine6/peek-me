from datetime import datetime, timezone
from functools import wraps
import logging
import os
from zoneinfo import ZoneInfo

import dotenv
from flask import Flask, request, jsonify

app = Flask(__name__)
token = ''
GLOBAL_TIMEZONE = ZoneInfo('Asia/Shanghai')

device_format_string = """
设备：{device_name}
- 正在使用的程序：{program_name}{extra_data}
- 更新时间：{time}
""".strip()

device_offline_string = """
设备：{device_name}
- 离线
- 更新时间：{time}
""".strip()

class Device:
    def __init__(self, device_name: str, online: bool=True):
        self.device_name: str = device_name
        self.online: bool = online
        self.program_name: str = ''
        self.extra_data: str = ''
        self.time_last_updated: datetime = datetime.now(GLOBAL_TIMEZONE)

    def update(self, program_name: str, extra_data: str=''):
        self.time_last_updated = datetime.now(GLOBAL_TIMEZONE)
        self.program_name = program_name
        self.extra_data = extra_data
    
    def to_string(self):
        return device_format_string.format(
            device_name=self.device_name,
            program_name=self.program_name,
            extra_data='\n- ' + self.extra_data if self.extra_data != '' else '',
            time=self.time_last_updated.strftime('%Y/%m/%d/ %H:%M:%S')
        )
    
    def to_dict(self):
        return {
            'device_name': self.device_name,
            'online': self.online,
            'program_name': self.program_name,
            'extra_data': self.extra_data,
            'time_last_updated': self.time_last_updated.isoformat()
        }

    def switch_online_state(self, state: bool=None):
        self.time_last_updated = datetime.now(GLOBAL_TIMEZONE)
        if state is None:
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
        return func(*args, **kwargs)
    return wrapper

def required_params(*params):
    def wrapper(f):
        @wraps(f)
        def decorated_func(*args, **kwargs):
            missing = [param for param in params if param not in request.form]
            if missing:
                return jsonify({
                    'error': f'Missing required parameter(s): {", ".join(missing)}',
                }), 400
            return f(*args, **kwargs)
        return decorated_func
    return wrapper

@app.route('/api/update', methods=['POST'])
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
    return jsonify({
        'message': f'Updated data of device {device_name}'
    }), 200

@app.route('/api/peek', methods=['POST'])
@verification_required
def peek():
    return_format = request.form.get('format', 'text')
    if return_format == 'text':
        lines = [device.to_string() for device in device_list.values()]
        return '\n'.join(lines), 200
    elif return_format == 'json':
        data = {device_name: device.to_dict() for device_name, device in device_list.items()}
        return jsonify(data), 200


if __name__ == '__main__':
    dotenv.load_dotenv()
    token = os.getenv('TOKEN')
    app.run()
    