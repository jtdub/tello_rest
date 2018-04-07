#!/usr/bin/env python3

from flask import Flask
from flask import request
from flask import json
import threading
import socket


app = Flask(__name__)
error = "{'error': 'invalid method'}"
result = ['INIT']
local_host = ('', 9000)
tello_host = ('192.168.10.1', 8889)
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


def tello_recv():
    while True:
        try:
            data, server = sock.recvfrom(1518)
            result[0] = data.decode(encoding="utf-8")
            return result
        except Exception:
            break

sock.bind(local_host)

tello_thread = threading.Thread(target=tello_recv)
tello_thread.start()

message = 'command'
message = message.encode(encoding="utf-8")
sock.sendto(message, tello_host)


@app.route('/api/v1/runway/<string:route>', methods=['POST'])
def runway(route):

    if request.method == 'POST':
        if route == 'status':
            return json.dumps({'flight_status': result[0]})
        elif route == 'takeoff':
            message = 'takeoff'.encode(encoding='utf-8')
            sock.sendto(message, tello_host)
            return json.dumps({'status': result[0]})
        elif route == 'land':
            message = 'land'.encode(encoding='utf-8')
            sock.sendto(message, tello_host)
            return json.dumps({'status': result[0]})
        else:
            return json.dumps(error)
    else:
        return json.dumps(error)

@app.route('/api/v1/altitude/<string:direction>', methods=['POST'])
def altitude(direction, distance):
    if request.method == 'POST':
       if (direction == 'up' or direction == 'down'):
           message = f'{direction} 20'
           message = message.encode(encoding='utf-8')
           sock.sendto(message, tello_host)
           return json.dumps({'status': result[0]})
       else:
           return json.dumps({'error': 'requires direction (up|down)'})
    else:
        return json.dumps(error)


if __name__ == "__main__":
    try:
        app.run()
    except KeyboardInterrupt:
        result[0] = 'CLOSE'
        sock.close()
