from random import choice

class EventTransition(object):
    def __init__(self,
                 source,
                 target,
                 event
                 ):
        self.source=source
        self.target=target
        self.event=event

    def __str__(self):
        return "source=" + str(self.source) + ", target=" + str(self.target) + ", event=" + self.event + "\n"
    
class DesAutomaton(object):
    def __init__(self,
                 initial_state,
                 accepting_states,
                 transitions,
                 events,
                 uc_events,
                 state_description_props,
                 product_automaton_labels=None):
        self.n_states=len(transitions)
        self.initial_state=initial_state
        self.accepting_states=accepting_states
        self.transitions=transitions
        self.events=events
        self.uc_events=uc_events
        self.state_description_props=state_description_props
        self.product_automaton_labels=product_automaton_labels
        
    def add_init_state(self):
        self.transitions.append([EventTransition(source=self.n_states,
                                                target=self.initial_state,
                                                event='init'
                                                )])
        self.events.append('init')
        self.state_description_props.append([])
        self.initial_state=self.n_states
        self.n_states+=1

        
    def __str__(self, print_trans=False):
        result="------DES model automaton info------\n"
        result+="States: " + str(self.n_states) + "\n"
        result+="Initial state: " + str(self.initial_state) + "\n"
        result+="Events: " + str(self.events) + "\n"
        result+="Uncontrollable events: " + str(self.uc_events) + "\n"
        result+="State description props: " + str(self.state_description_props) + "\n"
        result+="Transitions: \n"
        n_transitions=0   
        for source_state in self.transitions:
            for transition in source_state:
                if print_trans:
                    result+=str(transition)
                n_transitions+=1
        result+="Transitions: " + str(n_transitions) + "\n"
        if self.product_automaton_labels is not None:
            result+="\nProduct automaton labels: \n" + str(self.product_automaton_labels) + "\n"
        return result
    
    def print_dot(self):
        res='digraph G { \n rankdir=LR \n  node [shape="circle"] \n I [label="", style=invis, width=0] \n I -> '
        res+=str(self.initial_state) + "\n"
        for state in range(0,self.n_states):
            if self.product_automaton_labels is not None:
                res+=str(state) + ' [label = "' + str(state) + "\n" + str(self.product_automaton_labels[state]) + '\n' +  str(self.state_description_props[state]) + '"'
            else:
                res+=str(state) + ' [label = "' + str(state) + "\n" +  str(self.state_description_props[state]) + '"'
            if state in self.accepting_states:
                res+=', peripheries=2'
            res+=']\n'
            for transition in self.transitions[state]:
                res+=str(transition.source) + ' -> ' + str(transition.target) + ' [label="' + transition.event + '"]\n'
        res+='}'
        print(res)

    def random_run(self):
        state=self.initial_state
        while True:
            next_trans=choice(self.transitions[state])
            print(next_trans.event + '\n')
            state=next_trans.target
        

def parallel_composition(des_aut1, des_aut2):
    n_states=0
    initial_state=0
    accepting_states=[]
    product_labels=[]
    transitions=[]
    events=list(set(des_aut1.events) | set(des_aut2.events))
    uc_events=list(set(des_aut1.uc_events) | set(des_aut2.uc_events))
    shared_events=list(set(des_aut1.events) & set(des_aut2.events))
    state_labels_id_matrix=[[None for i in range(0,des_aut2.n_states)] for j in range(0,des_aut1.n_states)]
    state_description_props = []
    queue=[]
    queue.append([des_aut1.initial_state, des_aut2.initial_state])
    state_labels_id_matrix[des_aut1.initial_state][des_aut2.initial_state]=0
    while queue != []:
        state=queue.pop(0)
        product_labels.append(state)
        new_transitions=[]
        trans1=des_aut1.transitions[state[0]]
        trans2=des_aut2.transitions[state[1]]
        for transition1 in trans1:
            if transition1.event in shared_events:
                next_state=None
                for transition2 in trans2:
                    if transition1.event==transition2.event:
                        next_state=[transition1.target, transition2.target]
                if next_state is None:
                    continue
            else:
                next_state=[transition1.target, state[1]]
            next_state_id=state_labels_id_matrix[next_state[0]][next_state[1]]
            if next_state_id is None:
                queue.append(next_state)
                next_state_id=n_states+len(queue)
                state_labels_id_matrix[next_state[0]][next_state[1]]=next_state_id                
            #try:
                #next_state_id=(product_labels + queue).index(next_state)
            #except ValueError:
                #queue.append(next_state)
                #next_state_id=n_states+len(queue)                            
            new_transitions.append(EventTransition(source=n_states,
                                                    target=next_state_id,
                                                    event=transition1.event))
        for transition2 in trans2:
            if transition2.event not in shared_events:
                next_state=[state[0], transition2.target]
                next_state_id=state_labels_id_matrix[next_state[0]][next_state[1]]
                if next_state_id is None:
                    queue.append(next_state)
                    next_state_id=n_states+len(queue)
                    state_labels_id_matrix[next_state[0]][next_state[1]]=next_state_id
                    
                #try:
                    #next_state_id=(product_labels + queue).index(next_state) #bottleneck
                #except ValueError:
                    #queue.append(next_state)
                    #next_state_id=n_states+len(queue)                            
                new_transitions.append(EventTransition(source=n_states,
                                                        target=next_state_id,
                                                        event=transition2.event))

        state_description_props.append(list(set(des_aut1.state_description_props[state[0]]) | set(des_aut2.state_description_props[state[1]])))
        #if state[0] in des_aut1.accepting_states and state[1] in des_aut2.accepting_states:
         #   accepting_states.append(n_states)
        n_states+=1   
        transitions.append(new_transitions)
        
    return DesAutomaton(initial_state=initial_state,
                        accepting_states=accepting_states,
                        transitions=transitions,
                        events=events,
                        uc_events=uc_events,
                        state_description_props=state_description_props,
                        product_automaton_labels=product_labels)

def des_ltl_dfa_composition(des_dfa, ltl_dfa):
    n_states=0
    initial_state=0
    accepting_states=[]
    product_labels=[]
    transitions=[]
    events=list(des_dfa.events)
    uc_events=list(des_dfa.events)
    state_labels_id_matrix=[[None for i in range(0,ltl_dfa.n_states)] for j in range(0,des_dfa.n_states)]
    state_description_props=[]
    queue=[]
    queue.append([des_dfa.initial_state, ltl_dfa.initial_state])
    while queue != []:
        state=queue.pop(0)
        product_labels.append(state)
        new_transitions=[]
        trans_des=des_dfa.transitions[state[0]]
        trans_ltl=ltl_dfa.transitions[state[1]]
        for transition_ltl in trans_ltl:
            for transition_des in trans_des:
                true_props=des_dfa.state_description_props[transition_des.target] + [transition_des.event]
                if check_dnf_sat(transition_ltl.vector_dnf_label, true_props):
                    next_state=[transition_des.target, transition_ltl.target]
                    next_state_id=state_labels_id_matrix[next_state[0]][next_state[1]]
                    if next_state_id is None:
                        queue.append(next_state)
                        next_state_id=n_states+len(queue)
                        state_labels_id_matrix[next_state[0]][next_state[1]]=next_state_id
                    #try:
                        #next_state_id=(product_labels + queue).index(next_state)
                    #except ValueError:
                        #queue.append(next_state)
                        #next_state_id=n_states+len(queue)
                    new_transitions.append(EventTransition(source=n_states,
                                                           target=next_state_id,
                                                           event=transition_des.event))
                #else:
                    #print(true_props)
                    #print(transition_ltl.vector_dnf_label)
                    #print('------------------')
        state_description_props.append(list(des_dfa.state_description_props[state[0]]))
        if state[0] in des_dfa.accepting_states and state[1] in ltl_dfa.accepting_states:
            accepting_states.append(n_states)
        n_states+=1
        transitions.append(new_transitions)
        
    return DesAutomaton(initial_state=initial_state,
                        accepting_states=accepting_states,
                        transitions=transitions,
                        events=events,
                        uc_events=uc_events,
                        state_description_props=state_description_props,
                        product_automaton_labels=product_labels)        

def check_dnf_sat(vector_dnf_label, true_props):
    for conj_clause in vector_dnf_label:
        is_satisfied=True
        for (prop, value) in conj_clause.items():
            if value:
                if prop not in true_props:
                    is_satisfied=False
                    break
            else:
                if prop in conj_clause:
                    if prop in true_props:
                        is_satisfied=False
                        break
        if is_satisfied:
            return True
    return False
        
    
     