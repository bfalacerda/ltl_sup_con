import sys
import inspect
import os
sys.path.append(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))) + '/../../src') 

from copy import deepcopy
from ltl_dfa import LtlDfa
from symb_pn import SymbPetriNet
import symb_pn_compositions


pn=SymbPetriNet(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))) + "/pnml/ex2_new.xml")
pn.complete_prop_description()
pn.add_init_state()
n_robots=int(sys.argv[1])


formulas_list=[None for i in range(0, 4)]

formulas_list[0]='[] (( battery_high) -> (X (!dock && !go_to_docking_area && !stop_offering_guidance)))'
formulas_list[1]='[] (( !battery_high) -> (X ((! undock) && ((!go_to_playing_area && !offer_to_play && !go_to_reception_area && !offer_guidance) W charging))))'
formulas_list[2]='[] ((reached_playing_area) -> (X ((!go_to_reception_area) W (offer_to_play || dock))))'
formulas_list[3]='[] ((reached_reception_area) -> (X ((!go_to_playing_area) W (offer_guidance || dock))))'




##MONOLITHIC FULL FORMULA <- translation fails
#final='((' + formulas_list[0] + ')'
#for formula in formulas_list[1:]:
    #final+= ' && (' + formula + ')'
#final+=')'
#ltl_dfa=LtlDfa(final)
#res=symb_pn.symb_pn_ltl_dfa_composition(prod, ltl_dfa)
#print(res.n_places)
#print(len(res.transitions))
#res.remove_dead_trans_lola()
#print(res.n_places)
#print(len(res.transitions))


##INCREMENTAL MONOLITHIC
res=pn
print(res.n_places)
print(len(res.transitions))
#formulas_list=formulas_list[1:]+[formulas_list[0]]
for formula in formulas_list:
    ltl_dfa=LtlDfa(formula)
    res=symb_pn_compositions.symb_pn_ltl_dfa_composition(res,ltl_dfa)
    print(res.n_places)
    print(len(res.transitions))
    res.remove_dead_trans_lola()
    print(res.n_places)
    print(len(res.transitions))
    
res.remove_init_state()
##res.random_run(sleep_time=1)

pn_list=[deepcopy(res) for i in range(0,n_robots)]
for i in range(0,n_robots):
    pn_list[i].add_index(i)
   
prod=pn_list[0]
for i in range(1,n_robots):
    prod=symb_pn_compositions.parallel_composition(prod, pn_list[i])
    
#print(prod)

prod.add_init_state()
##print(ltl_dfa)

##prod.random_run()


formulas_list=[None for i in range(1 + n_robots)]

for j in range(0, n_robots):    
    formula='[] ((battery_high' + str(j) + ' && ('
    for i in range(0,n_robots):
        formula+='going_to_reception_area' + str(i) + ' || at_reception_area' + str(i) + ' || '
    formula=formula[:-4] + ')) -> (X (!stop_offering_to_play' + str(j) + ')))'
    formulas_list[j]=formula
    print(formula)

formula='[] (('
for i in range(0,n_robots):
    formula+='!going_to_reception_area' + str(i) + ' && !at_reception_area' + str(i) + ' && '
formula=formula[:-4] + ') -> (X ('
for i in range(0,n_robots):
    formula+='!go_to_playing_area' + str(i) + ' && !offer_to_play' + str(i) + ' && '
formula=formula[:-4]+')))'
formulas_list[-1]=formula
print(str(formulas_list))
    
##INCREMENTAL MONOLITHIC
res=prod
print(res.n_places)
print(len(res.transitions))
#formulas_list=[formulas_list[-1]]+formulas_list[:-1]
for formula in formulas_list:
    print(formula)
    ltl_dfa=LtlDfa(formula)
    res=symb_pn_compositions.symb_pn_ltl_dfa_composition(res,ltl_dfa)
    print("--------------------------\n\n\n")
    #print(res)
    print(res.n_places)
    print(len(res.transitions))
    #res.random_run(sleep_time=0)
    #res.remove_dead_trans_lola()
    #print(res.n_places)
    #print(len(res.transitions))  
    #print(res)
    #res.random_run(sleep_time=0)
    #res.remove_dead_trans_tina()    
##for formula in formulas_list:
    ##print(formula)

###MODULAR
##sup_list=[None for i in range(0, 2*n_robots+1)]
##i=0
##total=0
##total_trans=0
##total_trans_post_del=0
##for formula in formulas_list:
    ##ltl_dfa=LtlDfa(formula)
    ##res=symb_pn.symb_pn_ltl_dfa_composition(prod,ltl_dfa)
    ##print(res.n_places)
    ##print(len(res.transitions))
    ##total+=res.n_places
    ##total_trans+=len(res.transitions)
    ##res.remove_dead_trans_lola()
    ##sup_list[i]=res
    ##print(res.n_places)
    ##print(len(res.transitions))
    ##total_trans_post_del+=len(res.transitions)
    ##i+=1
##print("TOTAL=" + str(total))
##print("TOTALtrans=" + str(total_trans))
##print("TOTALtrans post del=" + str(total_trans_post_del))

##if True:
    ##res=sup_list[0]
    ##for sup in sup_list[1:]:
        ##print(res.n_places)
        ##print(len(res.transitions))
        ##res=symb_pn.parallel_composition(res,sup)
        ##res.remove_dead_trans_lola()
        ##print(res.n_places)
        ##print(len(res.transitions))


##print(ltl_dfa)

#res_dfa=res.build_reachability_dfa()
#res_dfa.print_dot()
#res.random_run()

