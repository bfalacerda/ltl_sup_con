import sys
import inspect
import os
sys.path.append(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))) + '/../src') #TODO: aprender a fazer isto como deve ser
import sys
from ltl_dfa import LtlDfa

arg = sys.argv[1]

ltl_dfa=LtlDfa(arg, print_dot=True)
print(str(ltl_dfa))
