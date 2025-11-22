#!/usr/bin/env python3
import json
import time
import requests

BASE = 'http://localhost:8000/api/v1'
results = {}

# Helper
def safe_json(r):
    try:
        return r.json()
    except Exception:
        return r.text

# 1) Try to register a fresh test user (use non-reserved domain), then login
# Log in as the CI user we inserted directly into the DB
token = None
try:
    login_payload = {'identifier': 'ci_user', 'password': 'password123'}
    r = requests.post(f"{BASE}/auth/login", json=login_payload, timeout=5)
    results['login_status'] = r.status_code
    results['login_body'] = safe_json(r)
    if r.status_code == 200:
        token = r.json().get('access_token')
except Exception as e:
    results['login_error'] = str(e)

# 3) List rooms
try:
    r = requests.get(f"{BASE}/rooms", timeout=5)
    results['rooms_status'] = r.status_code
    results['rooms_body'] = safe_json(r)
except Exception as e:
    results['rooms_error'] = str(e)

# 4) Create a room
room_id = None
if token:
    headers = {'Authorization': f'Bearer {token}'}
    try:
        r = requests.post(f"{BASE}/rooms", json={'name':'test-room','description':'created by testbot'}, headers=headers, timeout=5)
        results['create_room_status'] = r.status_code
        results['create_room_body'] = safe_json(r)
        if r.status_code in (200,201):
            body = r.json()
            room_id = body.get('id')
    except Exception as e:
        results['create_room_error'] = str(e)

# 5) WebSocket send/receive
ws_result = {}
if room_id and token:
    try:
        from websocket import create_connection
        ws_url = f"ws://localhost:8000/api/v1/ws/rooms/{room_id}?token={token}"
        ws = create_connection(ws_url, timeout=5)
        # Send a chat message according to server protocol
        msg = {'type': 'message', 'data': {'content': 'hello from testbot'}}
        ws.send(json.dumps(msg))
        # Try to receive a message (server may echo/broadcast)
        ws.settimeout(5)
        resp = ws.recv()
        try:
            ws_result['recv'] = json.loads(resp)
        except Exception:
            ws_result['recv_raw'] = resp
        ws.close()
    except Exception as e:
        ws_result['error'] = str(e)
else:
    ws_result['skipped'] = 'no room_id or token'

results['websocket'] = ws_result
print(json.dumps(results, indent=2))
