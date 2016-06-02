import sys
import inspect
import os
sys.path.append(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))) + '/../../src') #TODO: aprender a fazer isto como deve ser

from copy import deepcopy
from ltl_dfa import LtlDfa
from symb_pn import SymbPetriNet
from algebraic_pn import AlgPetriNet
import alg_pn_compositions
import pn_admis_check


pn=AlgPetriNet(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))) + "/pnml/ex2_new.xml")
print(pn)
pn.build_reachability_dfa().print_dot()
pn.complete_prop_description()
#pn.add_counter_place({'playing':1, '!charging':2})
pn.add_init_state()
pn.uc_events=['battery_below_3',
 'guidance_requested',
 'guidance_finished',
 'reached_reception_area',
 'battery_over_8',
 'play_requested',
 'play_finished',
 'reached_docking_area',
 'reached_playing_area']


n_robots=int(sys.argv[1])


formulas_list=[None for i in range(0, 4)]
spgecs_list=[None for i in range(0, 4)]

formulas_list[0]='[] (( battery_high) -> (X (!dock && !go_to_docking_area && !stop_offering_guidance)))'
spgecs_list[0]={'battery_high':['battery_high',1], '!battery_high':['!battery_high',1]}
formulas_list[1]='[] (( !battery_high) -> (X ((! undock) && ((!go_to_playing_area && !offer_to_play && !go_to_reception_area && !offer_guidance) W charging))))'
spgecs_list[1]={'battery_high':['battery_high',1], '!battery_high':['!battery_high',1],'charging':['charging',1], '!charging':['!charging',1]}
formulas_list[2]='[] ((reached_playing_area) -> (X ((!go_to_reception_area) W (offer_to_play || dock))))'
spgecs_list[2]={'reached_playing_area':['reached_playing_area',1], '!reached_playing_area':['!reached_playing_area',1]}
formulas_list[3]='[] ((reached_reception_area) -> (X ((!go_to_playing_area) W (offer_guidance || dock))))'
spgecs_list[3]={'reached_reception_area':['reached_reception_area',1], '!reached_reception_area':['!reached_reception_area',1]}




###MONOLITHIC FULL FORMULA <- translation fails
##final='((' + formulas_list[0] + ')'
##for formula in formulas_list[1:]:
    ##final+= ' && (' + formula + ')'
##final+=')'
##ltl_dfa=LtlDfa(final)
##res=symb_pn.symb_pn_ltl_dfa_composition(prod, ltl_dfa)
##print(res.n_places)
##print(len(res.transitions))
##res.remove_dead_trans_lola()
##print(res.n_places)
##print(len(res.transitions))


##INCREMENTAL MONOLITHIC
res=deepcopy(pn)
print(res.n_places)
print(len(res.transitions))
#formulas_list=formulas_list[1:]+[formulas_list[0]]
n_specs=1
for (formula, spgec_def) in zip(formulas_list, spgecs_list):
    ltl_dfa=LtlDfa(formula)
    res=alg_pn_compositions.alg_pn_ltl_dfa_composition(res,ltl_dfa,spgec_def,n_specs)
    #print(res.n_places)
    #print(len(res.transitions))
    res.remove_dead_trans_lola()
    #print(res.n_places)
    #print(len(res.transitions))
    n_specs+=1
    
trans_map=pn_admis_check.build_plant_sup_trans_map(pn, res)
mod_places=pn_admis_check.build_modified_places_mapping(pn, res, trans_map)
mod_places_obj=pn_admis_check.InputPlaceCombs(mod_places)

#for i in range(0, len(pn.transitions)):
    #trans=pn.transitions[i]
    #if trans.event in pn.uc_events:
        #place_ids=mod_places_obj.place_ids[i]
        #all_ks=mod_places_obj.all_ks[i]
        #for (mod_places, ks) in zip(place_ids, all_ks):
            #for k_tuple in ks:
                #partial_cover_marking=pn_admis_check.PartialCoverMarking(trans, res.n_places,  mod_places, k_tuple)
                #(new_sup, marking)=pn_admis_check.build_pn_from_partial_cover_marking(partial_cover_marking, res)
                #new_sup.check_reachability(marking)
                ##new_sup.remove_dead_trans_tina()

##new_sup.random_run(0)
#dfa=new_sup.build_reachability_dfa()
#dfa.print_dot()
    
##############AQUI    
res.remove_init_state()
##res.random_run(sleep_time=1)

pn_list=[deepcopy(res) for i in range(0,n_robots)]
for i in range(0,n_robots):
    pn_list[i].add_index(i)
   
prod=pn_list[0]
for i in range(1,n_robots):
    prod=alg_pn_compositions.parallel_composition(prod, pn_list[i])
    
#print(prod)

##print(ltl_dfa)


#prod.random_run()


formulas_list=[None for i in range(1 + n_robots)]
spgecs_list=[None for i in range(1 + n_robots)]

counter_place_def={}

for i in range(0, n_robots):
        counter_place_def['at_reception_area' + str(i)]=1
        counter_place_def['going_to_reception_area' + str(i)]=1
prod.add_counter_place(counter_place_def, "n_to_reception")

for j in range(0, n_robots):
    spgecs_list[j+1]={'battery_high' + str(j):['battery_high'+ str(j),1], 
                    '!battery_high'+ str(j):['!battery_high'+ str(j),1],
                    "at_least_one_to_reception":["n_to_reception",1],
                    "!at_least_one_to_reception":["!n_to_reception",2*n_robots]}
    formulas_list[j+1]='[] ((battery_high' + str(j) + ' && at_least_one_to_reception) -> (X (!stop_offering_to_play' + str(j) + ')))'
    
spgecs_list[0]={"at_least_one_to_reception":["n_to_reception",1],
                 "!at_least_one_to_reception":["!n_to_reception",2*n_robots]}
formula='[] ((!at_least_one_to_reception) -> (X ('
for i in range(0,n_robots):
    formula+='!go_to_playing_area' + str(i) + ' && !offer_to_play' + str(i) + ' && '
formula=formula[:-4]+')))'
formulas_list[0]=formula

print(str(formulas_list))
print(str(spgecs_list))


prod.add_init_state()
    
##INCREMENTAL MONOLITHIC
res=prod
print(res.n_places)
print(len(res.transitions))
#formulas_list=[formulas_list[-1]]+formulas_list[:-1]
i=0
for (formula, spgec_def) in zip(formulas_list, spgecs_list):
    print(formula)
    ltl_dfa=LtlDfa(formula)
    print(spgec_def)
    #modular=alg_pn_compositions.alg_pn_ltl_dfa_composition(prod,ltl_dfa,spgec_def,n_specs)
    res=alg_pn_compositions.alg_pn_ltl_dfa_composition(res,ltl_dfa,spgec_def,n_specs)
    print("--------------------------\n\n\n")
    #print(res)
    print(res.n_places)
    print(len(res.transitions))
    n_specs+=1
    #res.random_run(sleep_time=0)
    #res.remove_dead_trans_lola()
    #res.build_dead_trans_lp2(0)
    #if i==0:
        #break
    #i+=1
    #res.build_dead_trans_lp2(0)
    #print(res.n_places)
    #print(len(res.transitions))  
    #print(res)
    #res.random_run(sleep_time=0)
#print(res.generate_lola_string(False))    
##for formula in formulas_list:
    ##print(formula)
res.remove_dead_trans_tina()
for i in range(0, len(prod.transitions)):
    trans=pn.transitions[i]
    if trans.event in pn.uc_events:
        print(str(trans))
        place_ids=mod_places_obj.place_ids[i]
        all_ks=mod_places_obj.all_ks[i]
        for (mod_places, ks) in zip(place_ids, all_ks):
            for k_tuple in ks:
                partial_cover_marking=pn_admis_check.PartialCoverMarking(trans, res.n_places,  mod_places, k_tuple)
                (new_sup, marking)=pn_admis_check.build_pn_from_partial_cover_marking(partial_cover_marking, res)
                new_sup.check_reachability(marking)


###########AQUI


#res.remove_dead_trans_lola()
##MODULAR
#sup_list=[None for i in range(0, n_robots+1)]
#i=0
#total=0
#total_trans=0
#total_trans_post_del=0
#for (formula, spgec_def) in zip(formulas_list, spgecs_list):
    #ltl_dfa=LtlDfa(formula)
    #res=alg_pn_compositions.alg_pn_ltl_dfa_composition(prod,ltl_dfa, spgec_def,n_specs)
    #print(res.n_places)
    #print(len(res.transitions))
    #total+=res.n_places
    #total_trans+=len(res.transitions)
    #res.remove_dead_trans_lola()
    #sup_list[i]=res
    #print(res.n_places)
    #print(len(res.transitions))
    #total_trans_post_del+=len(res.transitions)
    #i+=1
    #n_specs+=1
#print("TOTAL=" + str(total))
#print("TOTALtrans=" + str(total_trans))
#print("TOTALtrans post del=" + str(total_trans_post_del))

#if True:
    #res=sup_list[0]
    #for sup in sup_list[1:]:
        #print(res.n_places)
        #print(len(res.transitions))
        #res=alg_pn_compositions.parallel_composition(res,sup)
        #res.remove_dead_trans_lola()
        #print(res.n_places)
        #print(len(res.transitions))


##print(ltl_dfa)

#res_dfa=res.build_reachability_dfa()
#res_dfa.print_dot()
#res.random_run()

