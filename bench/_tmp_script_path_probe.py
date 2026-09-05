
import json
import openrouter_tools as T
print(T.dispatch_tool_call('z3_verify', json.dumps({'claim': 'for all x: x > 0 implies x + 1 > 1'})))
