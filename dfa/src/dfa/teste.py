from ltl_dfa import LtlDfa
import symb_pn


a=[{'a':True},{'a':False,'b':True},{'c':False,'d':False,'e':False,'f':False}]
print(a)
print(symb_pn.check_dnf_sat(a,['c'],['d','a']))
print(a)