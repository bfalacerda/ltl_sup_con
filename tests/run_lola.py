from subprocess import Popen, PIPE
import json

net = b"""
PLACE p1, p2;
MARKING p1;
TRANSITION t
CONSUME p1;
PRODUCE p2;
"""

lola = Popen(["lola", '-f', 'AG NOT FIREABLE(t)', '--json', '--quiet'], stdin=PIPE, stdout=PIPE)
output = lola.communicate(input=net)
result = json.loads(output[0].decode())
print(result['analysis']['result'])
#net_has_deadlock = result['analysis']['result']