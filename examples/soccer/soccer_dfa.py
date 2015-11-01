import sys
import inspect
import os
sys.path.append(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))) + '/../../src') #TODO: aprender a fazer isto como deve ser
from ltl_dfa import LtlDfa
import des_dfa


n_robots=int(sys.argv[1])

dfa_list=[None for i in range(0,n_robots)]

for i in range(0,n_robots):
    n_states=9
    transitions=[[] for i in range(0,9)]
    state_description_props=[[] for i in range(0,9)]
    events=['move2ball',
            'close2ball',
            'getball',
            'blockedpath',
            'move2goal',
            'close2goal',
            'kickball',
            'startreceiving']
    events=list(map(lambda x: x + str(i), events))
    transitions[0].append(des_dfa.EventTransition(source=0,
                                                    target=1,
                                                    event='move2ball'+str(i)))
    transitions[0].append(des_dfa.EventTransition(source=0,
                                                    target=8,
                                                    event='startreceiving'+str(i)))
    transitions[1].append(des_dfa.EventTransition(source=1,
                                                    target=2,
                                                    event='close2ball'+str(i)))
    transitions[2].append(des_dfa.EventTransition(source=2,
                                                    target=3,
                                                    event='getball'+str(i)))
    transitions[3].append(des_dfa.EventTransition(source=3,
                                                    target=4,
                                                    event='blockedpath'+str(i)))
    transitions[3].append(des_dfa.EventTransition(source=3,
                                                    target=5,
                                                    event='move2goal'+str(i)))
    transitions[3].append(des_dfa.EventTransition(source=3,
                                                    target=6,
                                                    event='close2goal'+str(i)))
    transitions[5].append(des_dfa.EventTransition(source=5,
                                                    target=6,
                                                    event='close2goal'+str(i)))
    transitions[5].append(des_dfa.EventTransition(source=5,
                                                    target=4,
                                                    event='blockedpath'+str(i)))
    transitions[6].append(des_dfa.EventTransition(source=6,
                                                    target=0,
                                                    event='kickball'+str(i)))
    for j in range(0,n_robots):
        if j!=i:
            events.append('startpassing' + str(i) + str(j))
            events.append('pass' + str(i) + str(j))
            events.append('pass' + str(j) + str(i))
            transitions[4].append(des_dfa.EventTransition(source=4,
                                                        target=7,
                                                        event='startpassing'+str(i)+str(j))) 
            transitions[7].append(des_dfa.EventTransition(source=7,
                                                            target=0,
                                                            event='pass'+str(i)+str(j))) 
            transitions[8].append(des_dfa.EventTransition(source=8,
                                                            target=3,
                                                            event='pass'+str(j)+str(i))) 
    state_description_props[1]=['moving2ball'+str(i)]
    state_description_props[2]=['moving2ball'+str(i)]
    state_description_props[3]=['hasball'+str(i)]
    state_description_props[4]=['hasball'+str(i)]
    state_description_props[5]=['hasball'+str(i)]
    state_description_props[6]=['hasball'+str(i)]
    state_description_props[7]=['hasball'+str(i)]
    
    dfa_list[i]=des_dfa.DesAutomaton(initial_state=0,
                            accepting_states=range(0,9),
                            transitions=transitions,
                            events=events,
                            uc_events=[],
                            state_description_props=state_description_props,
                            product_automaton_labels=None)
    dfa_list[i].add_init_state()
    
dfa_list[0].print_dot()    
    
prod=dfa_list[0]
for i in range(1,n_robots):
    prod=des_dfa.parallel_composition(prod, dfa_list[i])
    
    
#prod.print_dot()    

            
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
    





#MONOLITHIC FULL FORMULA <- translation fails
final='((' + formulas_list[0] + ')'
for formula in formulas_list[1:]:
    final+= ' && (' + formula + ')'
final+=')'
ltl_dfa=LtlDfa(final)
res=des_dfa.des_ltl_dfa_composition(prod, ltl_dfa)


##INCREMENTAL MONOLITHIC
#res=prod
#print(res.n_states)
#for formula in formulas_list:
    #ltl_dfa=LtlDfa(formula)
    #res=des_dfa.des_ltl_dfa_composition(res,ltl_dfa)
    #print(res.n_states)

##MODULAR
#sup_list=[None for i in range(0, 2*n_robots+1)]
#i=0
#total=0
#for formula in formulas_list:
    #ltl_dfa=LtlDfa(formula)
    #res=des_dfa.des_ltl_dfa_composition(prod,ltl_dfa)
    #sup_list[i]=res
    #print(res.n_states)
    #total+=res.n_states
    #i+=1
#print("TOTAL=" + str(total))

#print(ltl_dfa)
#print(res)
res.print_dot()
#res.random_run()

