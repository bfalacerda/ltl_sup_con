from ltl_dfa import LtlDfa
import symb_pn
import sys



n_robots=int(sys.argv[1])

pn_list=[None for i in range(0,n_robots)]

for i in range(0,n_robots):
    initial_marking=[1,0,0,0,0,0,0,0,0,1,0,1,0]
    transitions=[]
    state_description_props=['moving2ball'+str(i), 'hasball'+str(i)]
    true_state_places={'moving2ball'+str(i):10, 'hasball'+str(i):12}
    false_state_places={'moving2ball'+str(i):9, 'hasball'+str(i):11}
    events=['move2ball',
            'close2ball',
            'getball',
            'blockedpath',
            'move2goal',
            'close2goal',
            'kickball',
            'startreceiving']
    events=list(map(lambda x: x + str(i), events))
    transitions.append(symb_pn.EventTransition(input_ids=[0,9],
                                            input_weights=[1, 1],
                                            output_ids=[1,10],
                                            output_weights=[1,1],
                                            event='move2ball'+str(i)))
    transitions.append(symb_pn.EventTransition(input_ids=[0],
                                            input_weights=[1],
                                            output_ids=[8],
                                            output_weights=[1],
                                            event='startreceiving'+str(i)))
    transitions.append(symb_pn.EventTransition(input_ids=[1],
                                            input_weights=[1],
                                            output_ids=[2],
                                            output_weights=[1],
                                            event='close2ball'+str(i)))
    transitions.append(symb_pn.EventTransition(input_ids=[2,10,11],
                                            input_weights=[1,1,1],
                                            output_ids=[3,9,12],
                                            output_weights=[1,1,1],
                                            event='getball'+str(i)))
    transitions.append(symb_pn.EventTransition(input_ids=[3],
                                            input_weights=[1],
                                            output_ids=[4],
                                            output_weights=[1],
                                            event='blockedpath'+str(i)))
    transitions.append(symb_pn.EventTransition(input_ids=[3],
                                            input_weights=[1],
                                            output_ids=[5],
                                            output_weights=[1],
                                            event='move2goal'+str(i)))
    transitions.append(symb_pn.EventTransition(input_ids=[3],
                                            input_weights=[1],
                                            output_ids=[6],
                                            output_weights=[1],
                                            event='close2goal'+str(i)))
    transitions.append(symb_pn.EventTransition(input_ids=[5],
                                            input_weights=[1],
                                            output_ids=[6],
                                            output_weights=[1],
                                            event='close2goal'+str(i)))
    transitions.append(symb_pn.EventTransition(input_ids=[5],
                                            input_weights=[1],
                                            output_ids=[4],
                                            output_weights=[1],
                                            event='blockedpath'+str(i)))
    transitions.append(symb_pn.EventTransition(input_ids=[6,12],
                                            input_weights=[1,1],
                                            output_ids=[0,11],
                                            output_weights=[1,1],
                                            event='kickball'+str(i)))
    for j in range(0,n_robots):
        if j!=i:
            events.append('startpassing' + str(i) + str(j))
            events.append('pass' + str(i) + str(j))
            events.append('pass' + str(j) + str(i))
            transitions.append(symb_pn.EventTransition(input_ids=[4],
                                            input_weights=[1],
                                            output_ids=[7],
                                            output_weights=[1],
                                            event='startpassing'+str(i)+str(j)))
            transitions.append(symb_pn.EventTransition(input_ids=[7,12],
                                            input_weights=[1,1],
                                            output_ids=[0,11],
                                            output_weights=[1,1],
                                            event='pass'+str(i)+str(j)))
            transitions.append(symb_pn.EventTransition(input_ids=[8,11],
                                            input_weights=[1,1],
                                            output_ids=[3,12],
                                            output_weights=[1,1],
                                            event='pass'+str(j)+str(i))) 
 
    pn_list[i]=symb_pn.SymbPetriNet(initial_marking=initial_marking,
                                events=events,
                                uc_events=events,
                                transitions=transitions,
                                state_description_props=state_description_props,
                                true_state_places=true_state_places,
                                false_state_places=false_state_places)
    pn_list[i].add_init_state()
    
    
prod=pn_list[0]
for i in range(1,n_robots):
    prod=symb_pn.parallel_composition(prod, pn_list[i])
    
    

formulas_list=[None for i in range(0, 2*n_robots+1)]

formula1='[] (('
for i in range(0,n_robots):
    formula1+= 'moving2ball' + str(i) + ' || hasball' + str(i) + ' || '
    
formula1=formula1[:-4] + ') -> X (!('

for i in range(0,n_robots):
    formula1+='move2ball' + str(i) + ' || '
    
formula1=formula1[:-4] + ')))'

formulas_list[0]=formula1

for i in range(0,n_robots):
    formula2='[] ((';
    for j in range(0,n_robots):
        if i != j:
            formula2+='startpassing' + str(j) + str(i) + ' || '
    formula2=formula2[:-4] + ')->(X (('
    formula2+='!move2ball' + str(i) + ' && !getball' + str(i) + ' && !move2goal' + str(i) + ' && !kickball' + str(i)
    for k in range(0,n_robots):
        if i != k:
            formula2+= ' && !startpassing' + str(i) + str(k) + ' && !pass' + str(i) + str(k)
    formula2+= ') W startreceiving' + str(i) + ')))'
    formulas_list[i+1]=formula2;

for i in range(0,n_robots):
    formula3='[](('
    for j in range(0,n_robots):
        if j != i:
            formula3+='!startpassing' + str(j) + str(i) + ' && '
    formula3=formula3[:-4] + ') -> (X !startreceiving' + str(i) + '))'
    formulas_list[n_robots+i+1]=formula3
    




##MONOLITHIC FULL FORMULA <- translation fails
#final='((' + formulas_list[0] + ')'
#for formula in formulas_list[1:]:
    #final+= ' && (' + formula + ')'
#final+=')'
#ltl_dfa=LtlDfa(final)
#ltl_dfa=LtlDfa(formulas_list[0])
#res=symb_pn.symb_pn_ltl_dfa_composition(prod, ltl_dfa)
#print(res.n_places)
#print(len(res.transitions))
#res.remove_dead_trans_lola()
#print(res.n_places)
#print(len(res.transitions))


##INCREMENTAL MONOLITHIC
#res=prod
#print(res.n_places)
#print(len(res.transitions))
##formulas_list=formulas_list[1:]+[formulas_list[0]]
#for formula in formulas_list:
    #ltl_dfa=LtlDfa(formula)
    #res=symb_pn.symb_pn_ltl_dfa_composition(res,ltl_dfa)
    #print(res.n_places)
    #print(len(res.transitions))
    #res.remove_dead_trans_lola()
    #print(res.n_places)
    #print(len(res.transitions))

#for formula in formulas_list:
    #print(formula)

#MODULAR
sup_list=[None for i in range(0, 2*n_robots+1)]
i=0
total=0
total_trans=0
total_trans_post_del=0
for formula in formulas_list:
    ltl_dfa=LtlDfa(formula)
    res=symb_pn.symb_pn_ltl_dfa_composition(prod,ltl_dfa)
    print(res.n_places)
    print(len(res.transitions))
    total+=res.n_places
    total_trans+=len(res.transitions)
    res.remove_dead_trans_lola()
    sup_list[i]=res
    print(res.n_places)
    print(len(res.transitions))
    total_trans_post_del+=len(res.transitions)
    i+=1
print("TOTAL=" + str(total))
print("TOTALtrans=" + str(total_trans))
print("TOTALtrans post del=" + str(total_trans_post_del))

#if True:
    #res=sup_list[0]
    #for sup in sup_list[1:]:
        #print(res.n_places)
        #print(len(res.transitions))
        #res=symb_pn.parallel_composition(res,sup)
        #res.remove_dead_trans_lola()
        #print(res.n_places)
        #print(len(res.transitions))


#print(ltl_dfa)
#print(res)

res_dfa=res.build_reachability_dfa()
res_dfa.print_dot()
#res.random_run()

