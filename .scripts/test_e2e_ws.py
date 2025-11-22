#!/usr/bin/env python3
import json, time
import requests
from websocket import create_connection

BASE = 'http://localhost:8000/api/v1'

# Helper
def safe_json(r):
    try:
        return r.json()
    except Exception:
        return r.text

# Create two CI users if not present (we'll attempt register then fallback to assume exist)
users = [
    {'username': 'ci_user_a', 'email': 'ci_user_a@localtest.me', 'password': 'password123'},
    {'username': 'ci_user_b', 'email': 'ci_user_b@localtest.me', 'password': 'password123'},
]

for u in users:
    try:
        r = requests.post(f"{BASE}/auth/register", json={'username': u['username'], 'email': u['email'], 'password': u['password']}, timeout=5)
    except Exception as e:
        print('register error', e)

# Login both users
tokens = {}
for u in users:
    try:
        r = requests.post(f"{BASE}/auth/login", json={'identifier': u['username'], 'password': u['password']}, timeout=5)
        print(u['username'], 'login status', r.status_code)
        if r.status_code == 200:
            tokens[u['username']] = r.json().get('access_token')
        else:
            print('login body', safe_json(r))
    except Exception as e:
        print('login exception', e)

# Create room using first user's token
room_id = None
if tokens.get('ci_user_a'):
    headers = {'Authorization': f"Bearer {tokens['ci_user_a']}"}
    try:
        r = requests.post(f"{BASE}/rooms", json={'name': 'e2e-room', 'description': 'e2e test room'}, headers=headers, timeout=5)
        print('create room status', r.status_code)
        if r.status_code in (200,201):
            room_id = r.json().get('id')
    except Exception as e:
        print('create room exception', e)

if not room_id:
    # Try to find existing room named e2e-room
    try:
        r = requests.get(f"{BASE}/rooms", timeout=5)
        for rm in r.json():
            if rm.get('name') == 'e2e-room':
                room_id = rm.get('id')
                break
    except Exception as e:
        print('rooms list error', e)

print('room_id', room_id)

# Connect both users via WebSocket and exchange messages
results = {}
if room_id and tokens.get('ci_user_a') and tokens.get('ci_user_b'):
    try:
        ws_a = create_connection(f"ws://localhost:8000/api/v1/ws/rooms/{room_id}?token={tokens['ci_user_a']}")
        ws_b = create_connection(f"ws://localhost:8000/api/v1/ws/rooms/{room_id}?token={tokens['ci_user_b']}")
        # Give server time to broadcast presence
        time.sleep(0.5)

        # A sends message
        msg_a = {'type': 'message', 'data': {'content': 'hello from A'}}
        ws_a.send(json.dumps(msg_a))

        # B should receive it
        ws_b.settimeout(5)
        recv_b = ws_b.recv()
        print('B received:', recv_b)

        # B replies
        msg_b = {'type': 'message', 'data': {'content': 'hi A, this is B'}}
        ws_b.send(json.dumps(msg_b))

        ws_a.settimeout(5)
        recv_a = ws_a.recv()
        print('A received:', recv_a)

        results['a_recv'] = recv_a
        results['b_recv'] = recv_b

        ws_a.close()
        ws_b.close()
    except Exception as e:
        results['error'] = str(e)
else:
    results['skipped'] = 'missing room_id or tokens'

print('\nFINAL:', json.dumps(results, indent=2))
