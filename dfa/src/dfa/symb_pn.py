import des_dfa
from random import choice
from time import sleep
import copy

class EventTransition(object):
    def __init__(self,
                 input_ids,
                 input_weights,
                 output_ids,
                 output_weights,
                 event
                 ):
        self.input_ids=input_ids
        self.input_weights=input_weights
        self.output_ids=output_ids
        self.output_weights=output_weights
        self.event=event

    def __str__(self):
        return "input ids=" + str(self.input_ids) + ", input_weights=" + str(self.input_weights) + " output ids=" + str(self.output_ids) + ", output_weights=" + str(self.output_weights) + ", event=" + self.event + "\n"
    
class SymbPetriNet(object):
    def __init__(self,
                 initial_marking,
                 events,
                 uc_events,
                 transitions,
                 state_description_props,
                 true_state_places,
                 false_state_places):
        self.n_places=len(initial_marking)
        self.initial_marking=initial_marking
        self.transitions=transitions
        self.events=events
        self.uc_events=uc_events
        self.state_description_props=state_description_props
        self.true_state_places=true_state_places #{state_description_place:place_id,...}
        self.false_state_places=false_state_places
       
        
    def add_init_state(self):
        input_ids=[self.n_places]
        input_weights=[1]
        output_ids=[]
        output_weights=[]
        i=0
        for n_tokens in self.initial_marking:
            if n_tokens>0:
                output_ids.append(i)
                output_weights.append(n_tokens)
            i+=1                
        self.transitions.append(EventTransition(input_ids=input_ids,
                                input_weights=input_weights,
                                output_ids=output_ids,
                                output_weights=output_weights,
                                event='init'))
        self.events.append('init')
        self.initial_marking=[0 for i in range(0,self.n_places)]
        self.initial_marking.append(1)
        self.n_places+=1

        
    def __str__(self, print_trans=True):
        result="------Symbolic PN model info------\n"
        result+="Places: " + str(self.n_places) + "\n"
        result+="Initial marking: " + str(self.initial_marking) + "\n"
        result+="Events: " + str(self.events) + "\n"
        result+="Uncontrollable events: " + str(self.uc_events) + "\n"
        result+="State description props: " + str(self.state_description_props) + "\n"
        result+="Transitions: \n"
        n_transitions=0   
        for transition in self.transitions:
                if print_trans:
                    result+=str(transition)
                n_transitions+=1
        result+="Transitions: " + str(n_transitions) + "\n"
        result+="True state description places:" + str(self.true_state_places) + "\n"
        result+="False state description places:" + str(self.false_state_places) + "\n"
        return result
    
    def build_reachability_dfa(self): #MIGHT BE BUGGY
        n_states=0
        initial_state=0
        product_labels=[]
        events=self.events
        state_description_props=[]
        queue=[self.initial_marking]
        transitions=[]
        
        while queue!=[]:
            new_transitions=[]
            marking=queue.pop(0)
            product_labels.append(marking)
            active_trans=self.get_active_transitions(marking)
            for transition in active_trans:
                next_marking=self.fire_transition(marking,transition)
                try:
                    next_marking_id=(product_labels + queue).index(next_marking)
                except ValueError:
                    queue.append(next_marking)
                    next_marking_id=n_states+len(queue)
                new_transitions.append(des_dfa.EventTransition(source=n_states,
                                                       target=next_marking_id,
                                                       event=transition.event))
            n_states+=1
            transitions.append(new_transitions)
                       
        state_description_props=[[] for i in range(0,n_states)]
        product_labels=state_description_props
        return des_dfa.DesAutomaton(initial_state=initial_state,
                        accepting_states=[],
                        transitions=transitions,
                        events=events,
                        uc_events=events,
                        state_description_props=state_description_props,
                        product_automaton_labels=product_labels)
        
        
    
    def get_active_transitions(self, marking):
        result=[]
        for transition in self.transitions:
            is_active=True
            for (input_id, input_weight) in zip(transition.input_ids, transition.input_weights):
                if marking[input_id]<input_weight:
                    is_active=False
                    break
            if is_active:
                result.append(transition)
        return result
    
    def fire_transition(self,current_marking,transition):
        marking=copy.deepcopy(current_marking)
        for (input_id, input_weight) in zip(transition.input_ids, transition.input_weights):
           marking[input_id]-=input_weight
        for (output_id, output_weight) in zip(transition.output_ids, transition.output_weights):
           marking[output_id]+=output_weight
        return marking

    def random_run(self):
        marking=self.initial_marking
        while True:
            active_trans=self.get_active_transitions(marking)
            next_trans=choice(active_trans)
            print([str(trans) for trans in active_trans])
            print(next_trans.event + '\n')
            marking=self.fire_transition(marking,next_trans)
        

def parallel_composition(symb_pn1, symb_pn2):

    n_places=symb_pn1.n_places+symb_pn2.n_places #assumes disjoint sets
    initial_marking=symb_pn1.initial_marking+symb_pn2.initial_marking
    transitions=[]
    events=list(set(symb_pn1.events) | set(symb_pn2.events))
    uc_events=list(set(symb_pn1.uc_events) | set(symb_pn2.uc_events))
    shared_events=list(set(symb_pn1.events) & set(symb_pn2.events))
    state_description_props = symb_pn1.state_description_props+symb_pn2.state_description_props #assumes disjoint sets
    
    transitions=[]
    for transition in symb_pn1.transitions:
        if transition.event in shared_events:
            for transition2 in symb_pn2.transitions:
                if transition.event==transition2.event:
                    input_ids=transition.input_ids+[input_id+symb_pn1.n_places for input_id in transition2.input_ids]
                    input_weights=transition.input_weights+transition2.input_weights
                    output_ids=transition.output_ids+[output_id+symb_pn1.n_places for output_id in transition2.output_ids]
                    output_weights=transition.output_weights+transition2.output_weights
                    transitions.append(EventTransition(input_ids=input_ids,
                                                    input_weights=input_weights,
                                                    output_ids=output_ids,
                                                    output_weights=output_weights,
                                                    event=transition.event))
        else:
            transitions.append(transition)
    
    for transition2 in symb_pn2.transitions:
        if transition2.event not in shared_events:
            input_ids=[input_id+symb_pn1.n_places for input_id in transition2.input_ids]
            input_weights=transition2.input_weights
            output_ids=[output_id+symb_pn1.n_places for output_id in transition2.output_ids]
            output_weights=transition2.output_weights
            transitions.append(EventTransition(input_ids=input_ids,
                                            input_weights=input_weights,
                                            output_ids=output_ids,
                                            output_weights=output_weights,
                                            event=transition2.event))
    
    true_state_places=symb_pn1.true_state_places.copy()
    false_state_places=symb_pn1.false_state_places.copy()
    true_state_places.update({key: value+symb_pn1.n_places for (key, value) in symb_pn2.true_state_places.items()})
    false_state_places.update({key: value+symb_pn1.n_places for (key, value) in symb_pn2.false_state_places.items()})
    
    return SymbPetriNet(initial_marking=initial_marking,
                 events=events,
                 uc_events=uc_events,
                 transitions=transitions,
                 state_description_props=state_description_props,
                 true_state_places=true_state_places,
                 false_state_places=false_state_places)

def symb_pn_ltl_dfa_composition(symb_pn, ltl_dfa):
    n_places=symb_pn.n_places+ltl_dfa.n_states
    init_marking_dfa=[0 for i in range(0,ltl_dfa.n_states)]
    init_marking_dfa[ltl_dfa.initial_state]=1
    initial_marking=symb_pn.initial_marking + init_marking_dfa
    events=symb_pn.events
    uc_events=symb_pn.uc_events
    state_description_props=symb_pn.state_description_props
    true_state_places=symb_pn.true_state_places
    false_state_places=symb_pn.false_state_places
    
    transitions=[]
    for pn_transition in symb_pn.transitions:
        (guaranteed_false_props, guaranteed_true_props)=get_guaranteed_prop_val(pn_transition, events, symb_pn.state_description_props,symb_pn.true_state_places,symb_pn.false_state_places)
        for state_transitions in ltl_dfa.transitions:
            for dfa_transition in state_transitions:
                missing_sat_dict=check_dnf_sat(dfa_transition.vector_dnf_label,guaranteed_false_props, guaranteed_true_props)
                if missing_sat_dict!=False:
                    if missing_sat_dict == True: 
                        conj_clause_input_places=[dfa_transition.source+symb_pn.n_places]
                        conj_clause_input_weights=[1]
                        conj_clause_output_places=[dfa_transition.target+symb_pn.n_places]
                        conj_clause_output_weights=[1]
                        transitions.append(EventTransition(input_ids=pn_transition.input_ids + conj_clause_input_places,
                                                        input_weights=pn_transition.input_weights + conj_clause_input_weights,
                                                        output_ids=pn_transition.output_ids + conj_clause_output_places,
                                                        output_weights=pn_transition.output_weights + conj_clause_output_weights,
                                                        event=pn_transition.event))
                    else:
                        for conj_clause in missing_sat_dict:
                            conj_clause_input_places=[dfa_transition.source+symb_pn.n_places]
                            conj_clause_input_weights=[1]
                            conj_clause_output_places=[dfa_transition.target+symb_pn.n_places]
                            conj_clause_output_weights=[1]
                            for (prop, value) in conj_clause.items():
                                if value:
                                    conj_clause_input_places.append(symb_pn.true_state_places[prop])
                                    conj_clause_output_places.append(symb_pn.true_state_places[prop])
                                else:
                                    conj_clause_input_places.append(symb_pn.false_state_places[prop])
                                    conj_clause_output_places.append(symb_pn.false_state_places[prop])
                                conj_clause_output_weights.append(1)
                                conj_clause_input_weights.append(1)
                            transitions.append(EventTransition(input_ids=pn_transition.input_ids + conj_clause_input_places,
                                                        input_weights=pn_transition.input_weights + conj_clause_input_weights,
                                                        output_ids=pn_transition.output_ids + conj_clause_output_places,
                                                        output_weights=pn_transition.output_weights + conj_clause_output_weights,
                                                        event=pn_transition.event))
                            
                 
             
    return SymbPetriNet(initial_marking=initial_marking,
                 events=events,
                 uc_events=uc_events,
                 transitions=transitions,
                 state_description_props=state_description_props,
                 true_state_places=true_state_places,
                 false_state_places=false_state_places)

def get_guaranteed_prop_val(pn_transition, events, state_description_props,true_state_places,false_state_places):
    guaranteed_true_props=[pn_transition.event]
    guaranteed_false_props=[event for event in events if event!=pn_transition.event]
    for prop in state_description_props:
        if true_state_places[prop] in pn_transition.output_ids:
            guaranteed_true_props.append(prop)
        if false_state_places[prop] in pn_transition.output_ids:
            guaranteed_false_props.append(prop)
    return (guaranteed_false_props, guaranteed_true_props)
     

def check_dnf_sat(original_vector_dnf_label, guaranteed_false_props, guaranteed_true_props):
    vector_dnf_label=copy.deepcopy(original_vector_dnf_label)
    for i in range(0,len(vector_dnf_label)):
        conj_clause=vector_dnf_label[i]
        if conj_clause != False:
            props_to_del=[]
            for (prop, value) in conj_clause.items(): 
                if value:
                    if prop in guaranteed_true_props:
                        props_to_del.append(prop)
                    elif prop in guaranteed_false_props:
                        vector_dnf_label[i]=False
                        break
                else:
                    if prop in guaranteed_false_props:
                        props_to_del.append(prop)
                    elif prop in guaranteed_true_props:
                        vector_dnf_label[i]=False
                        break
            if vector_dnf_label[i]!=False:
                for prop in props_to_del:
                    del(vector_dnf_label[i][prop])
        if vector_dnf_label[i] == {}:
            return True
    i=0
    while i<len(vector_dnf_label):        
        if vector_dnf_label[i]==False:
            del(vector_dnf_label[i])
        else:
            i+=1


    if vector_dnf_label==[]:
        return False
    else:
        return vector_dnf_label
        
    
     