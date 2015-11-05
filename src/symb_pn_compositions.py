from petri_net import EventTransition
from symb_pn import SymbPetriNet
import copy

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
        
    
     