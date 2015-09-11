import automaton


        
events1=['e1','e2']
state_description_props1=[['a','b'], ['c']]
print(state_description_props1)

t11=automaton.EventTransition(source=0,
                            target=1,
                            event='e1')
t12=automaton.EventTransition(source=1,
                            target=0,
                            event='e2')

aut1=automaton.DesAutomaton(initial_state=0,
                            transitions=[[t11],[t12]],
                            events=events1,
                            state_description_props=state_description_props1,
                            product_automaton_labels=None)


events2=['e2','e3', 'e4']
state_description_props2=[['d'], []]
t21=automaton.EventTransition(source=0,
                            target=1,
                            event='e3')
t22=automaton.EventTransition(source=1,
                            target=0,
                            event='e2')
t23=automaton.EventTransition(source=1,
                            target=1,
                            event='e4')

aut2=automaton.DesAutomaton(initial_state=0,
                            transitions=[[t21],[t22, t23]],
                            events=events2,
                            state_description_props=state_description_props2,
                            product_automaton_labels=None)

prod=automaton.parallel_composition(aut1,aut2)
print(prod)