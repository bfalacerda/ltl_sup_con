import sys
import inspect
import os
sys.path.append(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))) + '/../src') #TODO: aprender a fazer isto como deve ser
import des_dfa


events1=['e1','e2']
state_description_props1=[['a','b'], ['c']]
print(state_description_props1)

t11=des_dfa.EventTransition(source=0,
                            target=1,
                            event='e1')
t12=des_dfa.EventTransition(source=1,
                            target=0,
                            event='e2')

aut1=des_dfa.DesAutomaton(initial_state=0,
                            accepting_states=range(0,2),
                            transitions=[[t11],[t12]],
                            events=events1,
                            uc_events=['e2'],
                            state_description_props=state_description_props1,
                            product_automaton_labels=None)


events2=['e2','e3', 'e4']
state_description_props2=[['d'], []]
t21=des_dfa.EventTransition(source=0,
                            target=1,
                            event='e3')
t22=des_dfa.EventTransition(source=1,
                            target=0,
                            event='e2')
t23=des_dfa.EventTransition(source=1,
                            target=1,
                            event='e4')

aut2=des_dfa.DesAutomaton(initial_state=0,
                            accepting_states=range(0,2),
                            transitions=[[t21],[t22, t23]],
                            events=events2,
                            uc_events=[],
                            state_description_props=state_description_props2,
                            product_automaton_labels=None)

prod=des_dfa.parallel_composition(aut1,aut2)
print(prod)