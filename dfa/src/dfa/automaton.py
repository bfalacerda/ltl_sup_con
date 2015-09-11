class DnfTransitionDef(object):
    def __init__(self, 
                source=None,
                target=None,
                #string_label='',
                atomic_propositions=set(),
                vector_dnf_label=[] #((a & b) | (!c & d)) -> [{'a':True, 'b':True},{'c':False, 'd':True}]
                ): 
        self.source=source
        self.target=target
        #self.string_label=string_label
        self.atomic_propositions=atomic_propositions
        self.vector_dnf_label=vector_dnf_label
        
    def __str__(self):
        return "---- Transition info ----\n source: " + str(self.source) + "\n target: " + str(self.target) + "\n atomic_propositions: " + str(self.atomic_propositions) + "\n DNF label: " + str(self.vector_dnf_label) + "\n"


class CoSafeLtlAutomaton(object):
    def __init__(self, hoa_string):
        self.n_states=0
        self.initial_state=0
        self.accepting_states=[]
        self.transitions=[]
        self.atomic_propositions=[]
        
        hoa_string=hoa_string.split('\n')
        
        current_state=0
        i=0;
        line=None
        while line != '--END--':
            line=hoa_string[i]
            line=line.split(': ')
            if line[0]=='States':
                self.n_states=int(line[1])
                self.transitions=[[] for i in range(0,self.n_states)]
            elif line[0]=='Start':
                self.initial_state=int(line[1])
            elif line[0]=='AP':
                self.atomic_propositions=[i.strip('"') for i in line[1].split(' ')[1:]]
            elif line[0]=='State':
                line=line[1].split(' ')
                if current_state != int(line[0]):
                    print("ERROR")
                if '{' in line[-1]:
                    self.accepting_states.append(current_state)
                i+=1
                line=hoa_string[i]
                while 'State:' not in line:
                    if line == '--END--':
                        break
                    line=line.split(' ')
                    
                    transition=DnfTransitionDef(source=current_state,
                                                target=int(line[-1]),
                                                atomic_propositions=set(),
                                                vector_dnf_label=[]
                                                )
                    for conj_clause_string in line[:-1]:
                        conj_clause_rep={}
                        conj_clause_string=conj_clause_string.strip('[')
                        conj_clause_string=conj_clause_string.strip(']')
                        if conj_clause_string=='t':
                            transition.atomic_propositions=None
                            transition.vector_dnf_label=True
                            continue
                        if conj_clause_string == '|':
                            continue
                        conj_clause_string=conj_clause_string.split('&')
                        for literal_id in conj_clause_string:
                            if '!' in literal_id:
                                literal=self.atomic_propositions[int(literal_id[1:])]
                                transition.atomic_propositions.add(literal)
                                conj_clause_rep[literal]=False
                            else:
                                literal=self.atomic_propositions[int(literal_id)]
                                transition.atomic_propositions.add(literal)
                                conj_clause_rep[literal]=True
                        transition.vector_dnf_label.append(conj_clause_rep)                                                   
                    self.transitions[current_state].append(transition)
                    i+=1
                    line=hoa_string[i]
                current_state+=1
                continue
                    
            i+=1
        print(self)
        
    def __str__(self):
        result="------Co-safe LTL automaton info------\n"
        result+="States: " + str(self.n_states) + "\n"
        result+="Initial state: " + str(self.initial_state) + "\n"
        result+="Accepting states: " + str(self.accepting_states) + "\n"
        result+="Atomic propositions: " + str(self.atomic_propositions) + "\n"
        result+="Transitions: \n"
        for source_state in self.transitions:
            for transition in source_state:
                result+=str(transition)
        return result
    
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
                 transitions,
                 events,
                 state_description_props,
                 product_automaton_labels=None):
        self.n_states=len(transitions)
        self.initial_state=initial_state
        self.transitions=transitions
        self.events=events
        self.state_description_props=state_description_props
        self.product_automaton_labels=product_automaton_labels
        
    def __str__(self):
        result="------DES model automaton info------\n"
        result+="States: " + str(self.n_states) + "\n"
        result+="Initial state: " + str(self.initial_state) + "\n"
        result+="Events: " + str(self.events) + "\n"
        result+="State description props: " + str(self.state_description_props) + "\n"
        result+="Transitions: \n"
        for source_state in self.transitions:
            for transition in source_state:
                result+=str(transition)                
        if self.product_automaton_labels is not None:
            result+="\nProduct automaton labels: \n" + str(self.product_automaton_labels) + "\n"
        return result
        

def parallel_composition(des_aut1, des_aut2):
    print(des_aut1.state_description_props)
    n_states=0
    initial_state=0
    product_labels=[]
    transitions=[]
    events=list(set(des_aut1.events) | set(des_aut2.events))
    shared_events=list(set(des_aut1.events) & set(des_aut2.events))
    state_description_props = []
    queue=[]
    queue.append([des_aut1.initial_state, des_aut2.initial_state])
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
            try:
                next_state_id=(product_labels + queue).index(next_state)
            except ValueError:
                queue.append(next_state)
                next_state_id=n_states+len(queue)                            
            new_transitions.append(EventTransition(source=n_states,
                                                    target=next_state_id,
                                                    event=transition1.event))
        for transition2 in trans2:
            if transition2.event not in shared_events:
                next_state=[state[0], transition2.target]
                try:
                    next_state_id=(product_labels + queue).index(next_state)
                except ValueError:
                    queue.append(next_state)
                    next_state_id=n_states+len(queue)                            
                new_transitions.append(EventTransition(source=n_states,
                                                        target=next_state_id,
                                                        event=transition2.event))

        state_description_props.append(list(set(des_aut1.state_description_props[state[0]]) | set(des_aut2.state_description_props[state[1]])))
        n_states+=1   
        transitions.append(new_transitions)
        
    return DesAutomaton(initial_state=initial_state,
                        transitions=transitions,
                        events=events,
                        state_description_props=state_description_props,
                        product_automaton_labels=product_labels)
                        
    
    
    
     