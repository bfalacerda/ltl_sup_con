from petri_net import EventTransition
from algebraic_pn import AlgPetriNet
import copy

def parallel_composition(alg_pn1, alg_pn2):
    n_places=alg_pn1.n_places+alg_pn2.n_places #assumes disjoint sets
    place_names=alg_pn1.place_names+alg_pn2.place_names
    initial_marking=alg_pn1.initial_marking+alg_pn2.initial_marking
    transitions=[]
    events=list(set(alg_pn1.events) | set(alg_pn2.events))
    uc_events=list(set(alg_pn1.uc_events) | set(alg_pn2.uc_events))
    shared_events=list(set(alg_pn1.events) & set(alg_pn2.events))
    bounded_places_descriptors=alg_pn1.bounded_places_descriptors+alg_pn2.bounded_places_descriptors#assumes disjoint sets
    place_bounds=alg_pn1.place_bounds.copy()
    place_bounds.update(alg_pn2.place_bounds)
           
    transitions=[]
    for transition in alg_pn1.transitions:
        if transition.event in shared_events:
            for transition2 in alg_pn2.transitions:
                if transition.event==transition2.event:
                    input_ids=transition.input_ids+[input_id+alg_pn1.n_places for input_id in transition2.input_ids]
                    input_weights=transition.input_weights+transition2.input_weights
                    output_ids=transition.output_ids+[output_id+alg_pn1.n_places for output_id in transition2.output_ids]
                    output_weights=transition.output_weights+transition2.output_weights
                    transitions.append(EventTransition(input_ids=input_ids,
                                                    input_weights=input_weights,
                                                    output_ids=output_ids,
                                                    output_weights=output_weights,
                                                    event=transition.event))
        else:
            transitions.append(transition)
    
    for transition2 in alg_pn2.transitions:
        if transition2.event not in shared_events:
            input_ids=[input_id+alg_pn1.n_places for input_id in transition2.input_ids]
            input_weights=transition2.input_weights
            output_ids=[output_id+alg_pn1.n_places for output_id in transition2.output_ids]
            output_weights=transition2.output_weights
            transitions.append(EventTransition(input_ids=input_ids,
                                            input_weights=input_weights,
                                            output_ids=output_ids,
                                            output_weights=output_weights,
                                            event=transition2.event))
    
    positive_bounded_places=alg_pn1.positive_bounded_places.copy()
    complement_bounded_places=alg_pn1.complement_bounded_places.copy()
    positive_bounded_places.update({key: value+alg_pn1.n_places for (key, value) in alg_pn2.positive_bounded_places.items()})
    complement_bounded_places.update({key: value+alg_pn1.n_places for (key, value) in alg_pn2.complement_bounded_places.items()})
    
    return AlgPetriNet(initial_marking=initial_marking,
                       place_names=place_names,
                       events=events,
                       uc_events=uc_events,
                       transitions=transitions,
                       bounded_places_descriptors=bounded_places_descriptors,
                       place_bounds=place_bounds,
                       positive_bounded_places=positive_bounded_places,
                       complement_bounded_places=complement_bounded_places)


def alg_pn_ltl_dfa_composition(alg_pn, ltl_dfa, props_to_spgeq, n_spec):
    n_places=alg_pn.n_places
    initial_marking=alg_pn.initial_marking.copy()
    place_names=alg_pn.place_names.copy()
    bounded_places_descriptors=alg_pn.bounded_places_descriptors.copy()
    place_bounds=alg_pn.place_bounds.copy()
    positive_bounded_places=alg_pn.positive_bounded_places.copy()
    complement_bounded_places=alg_pn.complement_bounded_places.copy()
    for i in range(0, ltl_dfa.n_states):
        if i==ltl_dfa.initial_state:
            initial_marking.append(1)
        else:
            initial_marking.append(0)
        dfa_place_name='dfa' + str(n_spec) + '_' + str(i)
        place_names.append(dfa_place_name)
        bounded_places_descriptors.append(dfa_place_name)
        place_bounds[dfa_place_name]=1
        positive_bounded_places[dfa_place_name]=n_places
        n_places=n_places+1
    events=alg_pn.events
    uc_events=alg_pn.uc_events
    
    if alg_pn.prod_trans_ids==[]:
        original_trans_ids=[i for i in range(0,len(alg_pn.transitions))]
    else:
        original_trans_ids=[prod_trans_id[0] for prod_trans_id in alg_pn.prod_trans_ids]
    
    
    prod_trans_ids=[]
    pn_trans_id=0
    transitions=[]
    for pn_transition in alg_pn.transitions:
        for state_transitions in ltl_dfa.transitions:
            dfa_trans_id=0
            for dfa_transition in state_transitions:
                missing_sat_dict=evaluate_events(dfa_transition.vector_dnf_label, pn_transition, alg_pn.events)
                if  missing_sat_dict!=False:
                    dfa_trans_input_places=[dfa_transition.source+alg_pn.n_places]
                    dfa_trans_input_weights=[1]
                    dfa_trans_output_places=[dfa_transition.target+alg_pn.n_places]
                    dfa_trans_output_weights=[1]
                    if missing_sat_dict == True:                         
                        transitions.append(EventTransition(input_ids=pn_transition.input_ids + dfa_trans_input_places,
                                                        input_weights=pn_transition.input_weights + dfa_trans_input_weights,
                                                        output_ids=pn_transition.output_ids + dfa_trans_output_places,
                                                        output_weights=pn_transition.output_weights + dfa_trans_output_weights,
                                                        event=pn_transition.event))
                        prod_trans_ids.append([original_trans_ids[pn_trans_id], dfa_trans_id])
                    else:
                        trans_array=[]
                        for conj_clause in missing_sat_dict:
                            min_sat_trans=build_min_sat_trans(conj_clause, pn_transition, alg_pn.place_bounds, alg_pn.positive_bounded_places, alg_pn.complement_bounded_places, props_to_spgeq)
                            if min_sat_trans == pn_transition:
                                trans_array=[min_sat_trans]
                                break
                            elif min_sat_trans != False:
                                trans_array.append(min_sat_trans)
                        for min_sat_trans in trans_array:
                            transitions.append(EventTransition(input_ids=min_sat_trans.input_ids + dfa_trans_input_places,
                                                            input_weights=min_sat_trans.input_weights + dfa_trans_input_weights,
                                                            output_ids=min_sat_trans.output_ids + dfa_trans_output_places,
                                                            output_weights=min_sat_trans.output_weights + dfa_trans_output_weights,
                                                            event=min_sat_trans.event))
                            prod_trans_ids.append([original_trans_ids[pn_trans_id], dfa_trans_id])
                dfa_trans_id+=1
        pn_trans_id+=1
    return AlgPetriNet(initial_marking=initial_marking,
                       place_names=place_names,
                       events=events,
                       uc_events=uc_events,
                       transitions=transitions,
                       bounded_places_descriptors=bounded_places_descriptors,
                       place_bounds=place_bounds,
                       positive_bounded_places=positive_bounded_places,
                       complement_bounded_places=complement_bounded_places,
                       prod_trans_ids=prod_trans_ids)

    


def build_min_sat_trans(conj_clause, pn_transition, place_bounds, positive_bounded_places, complement_bounded_places, props_to_spgeq):
    min_sat_trans=EventTransition(input_ids=pn_transition.input_ids.copy(),
                                  input_weights=pn_transition.input_weights.copy(),
                                  output_ids=pn_transition.output_ids.copy(),
                                  output_weights=pn_transition.output_weights.copy(),
                                  event=pn_transition.event)
    for (key,value) in conj_clause.items():
        if value:
            place_index=positive_bounded_places[props_to_spgeq[key][0]]
            comp_place_index=complement_bounded_places[props_to_spgeq[key][0]]
            min_tokens=props_to_spgeq[key][1]
        else:
            place_index=complement_bounded_places[props_to_spgeq[key][0]]
            comp_place_index=positive_bounded_places[props_to_spgeq[key][0]]
            min_tokens=props_to_spgeq['!' + key][1]
        bound=place_bounds[props_to_spgeq[key][0]]
        input_weight=get_weight(min_sat_trans.input_ids, min_sat_trans.input_weights, place_index)
        output_weight_to_complement=get_weight(min_sat_trans.output_ids, min_sat_trans.output_weights, comp_place_index)
        output_weight=get_weight(min_sat_trans.output_ids, min_sat_trans.output_weights, place_index)
        
        if bound - max(input_weight, output_weight_to_complement) + output_weight < min_tokens:
            return False
        elif  min_tokens>output_weight:
            new_input_weight=min_tokens + input_weight - output_weight
            new_output_weight=min_tokens
            if input_weight==0:
                min_sat_trans.input_ids.append(place_index)
                min_sat_trans.input_weights.append(new_input_weight)
            else:    
                input_index=min_sat_trans.input_ids.index(place_index)
                min_sat_trans.input_weights[input_index]=new_input_weight
            if output_weight==0:    
                min_sat_trans.output_ids.append(place_index)
                min_sat_trans.output_weights.append(new_output_weight)
            else:
                output_index=min_sat_trans.output_ids.index(place_index)
                min_sat_trans.output_weights[output_index]=new_output_weight
    return min_sat_trans

def get_weight(ids, weights, index):
    if index in ids:
        return weights[ids.index(index)]
    else:
        return 0


def evaluate_events(vector_dnf_label, pn_transition, pn_events):
    res=copy.deepcopy(vector_dnf_label)
    for i in range(0, len(res)):
        conj_clause=res[i]
        events_to_del=[]
        for (key,value) in conj_clause.items():
            if key in pn_events:
                if value:
                    if key == pn_transition.event:
                        events_to_del.append(key)
                    else:
                        res[i]=False
                        break
                else:
                    if key != pn_transition.event:
                        events_to_del.append(key)
                    else:
                       res[i]=False
                       break
        if res[i] != False:
            for event in events_to_del:
                del(res[i][event])
        if res[i]=={}:
            return True    
    i=0
    while i<len(res):        
        if res[i]==False:
            del(res[i])
        else:
            i+=1
    if res==[]:
        return False
    else:
        return res
        
       

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
        
    
     