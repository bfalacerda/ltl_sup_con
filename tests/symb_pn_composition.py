import sys
import inspect
import os
sys.path.append(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))) + '/../src') #TODO: aprender a fazer isto como deve ser
from symb_pn import SymbPetriNet, EventTransition
import symb_pn_compositions


initial_marking1=[1,0]
events1=['e1','e2']
uc_events1=events1
state_description_props1=['in_p1']
true_state_places1={'in_p1':0}
false_state_places1={'in_p1':1}


t11=EventTransition(input_ids=[0],
                            input_weights=[1],
                            output_ids=[1],
                            output_weights=[1],
                            event='e1')
t12=EventTransition(input_ids=[1],
                            input_weights=[1],
                            output_ids=[0],
                            output_weights=[1],
                            event='e2')

transitions1=[t11,t12]

pn1=SymbPetriNet(initial_marking=initial_marking1,
                        events=events1,
                        uc_events=uc_events1,
                        transitions=transitions1,
                        state_description_props=state_description_props1,
                        true_state_places=true_state_places1,
                        false_state_places=false_state_places1)

initial_marking2=[1,1]
events2=['e3','e2','e4']
uc_events2=events2
state_description_props2=['in_p3']
true_state_places2={'in_p3':0}
false_state_places2={'in_p3':1}


t21=EventTransition(input_ids=[0],
                            input_weights=[1],
                            output_ids=[1],
                            output_weights=[1],
                            event='e3')
t22=EventTransition(input_ids=[1],
                            input_weights=[1],
                            output_ids=[0],
                            output_weights=[1],
                            event='e2')
t23=EventTransition(input_ids=[1],
                            input_weights=[2],
                            output_ids=[1],
                            output_weights=[2],
                            event='e4')

transitions2=[t21,t22, t23]

pn2=SymbPetriNet(initial_marking=initial_marking2,
                        events=events2,
                        uc_events=uc_events2,
                        transitions=transitions2,
                        state_description_props=state_description_props2,
                        true_state_places=true_state_places2,
                        false_state_places=false_state_places2)


prod=symb_pn_compositions.parallel_composition(pn1,pn2)
prod.remove_dead_trans_lola()
#print(prod)
#prod.print_lola()
#prod.random_run()