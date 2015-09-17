import sys
from ltl_dfa import LtlDfa

arg = sys.argv[1]

ltl_dfa=LtlDfa(arg, print_dot=True)
print(str(ltl_dfa))
