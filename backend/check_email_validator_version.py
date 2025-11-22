import importlib.metadata as m
try:
    print(m.version('email-validator'))
except Exception as e:
    print('error:', e)
