from petri_net import EventTransition, PetriNet
from symb_pn import SymbPetriNet
import copy
from itertools import product

class InputPlaceCombs(object):
    def __init__(self, mod_places):
        
        flatten_triples = lambda position: [[[mod_places[k][j][i][position] for i in range(0,len (mod_places[k][j]))] for j in range(0, len(mod_places[k]))] for k in range(0, len(mod_places))]
        
        place_ids=flatten_triples(0)
        plant_input_weights=flatten_triples(2)
        sup_input_weights=flatten_triples(1)
        self.place_ids=[list(product(*vector)) for vector in place_ids]
        self.plant_input_weights=[list(product(*vector)) for vector in plant_input_weights]
        self.sup_input_weights=[list(product(*vector)) for vector in sup_input_weights]
        
        self.clean_repeated_place_ids()
        self.all_ks=copy.deepcopy(self.place_ids)
        self.build_ks_vectors()

        
    def clean_repeated_place_ids(self):
        for trans_it in range(0, len(self.place_ids)):
                for tuple_it in range(0, len(self.place_ids[trans_it])):
                    i=0
                    while i < len(self.place_ids[trans_it][tuple_it]):                       
                        j=i+1
                        del_i=False
                        while j < len(self.place_ids[trans_it][tuple_it]):
                            if self.place_ids[trans_it][tuple_it][i] == self.place_ids[trans_it][tuple_it][j]:
                                self.place_ids[trans_it][tuple_it]=list(self.place_ids[trans_it][tuple_it])
                                self.plant_input_weights[trans_it][tuple_it]=list(self.plant_input_weights[trans_it][tuple_it])
                                self.sup_input_weights[trans_it][tuple_it]=list(self.sup_input_weights[trans_it][tuple_it])
                                if self.sup_input_weights[trans_it][tuple_it][i] <= self.sup_input_weights[trans_it][tuple_it][j]:
                                    del(self.place_ids[trans_it][tuple_it][j])
                                    del(self.plant_input_weights[trans_it][tuple_it][j])
                                    del(self.sup_input_weights[trans_it][tuple_it][j])
                                else:
                                    del(self.place_ids[trans_it][tuple_it][i])
                                    del(self.plant_input_weights[trans_it][tuple_it][i])
                                    del(self.sup_input_weights[trans_it][tuple_it][i])
                                    del_i=True
                                    break
                            else:
                                j=j+1
                        if not del_i:
                            i=i+1
                                    
                                 
    def build_ks_vectors(self):        
        for trans_it in range(0, len(self.place_ids)):
            for tuple_it in range(0, len(self.place_ids[trans_it])):
                plant_input_weights=self.plant_input_weights[trans_it][tuple_it]
                sup_input_weights=self.sup_input_weights[trans_it][tuple_it]
                k_vector=[]
                for (plant_input_weight, sup_input_weight) in zip(plant_input_weights, sup_input_weights):
                    k_vector.append(range(plant_input_weight, sup_input_weight))    
                self.all_ks[trans_it][tuple_it]=list(product(*k_vector))



class PartialCoverMarking(object):
    def __init__(self,plant_trans, n_sup_places,  place_ids=[], k_tuple=[]):
        self.marking=[0 for i in range(0, n_sup_places)]
        self.equal_place_ids=place_ids
        for (input_id, input_weight) in zip(plant_trans.input_ids, plant_trans.input_weights):
            self.marking[input_id]=input_weight
        for (place_id, k) in zip(place_ids, k_tuple):
            self.marking[place_id]=k
            


def get_associated_trans(plant_trans_id, sup):
    res=[]
    for (trans, original_trans_id) in zip(sup.transitions, sup.prod_trans_ids):
        if plant_trans_id == original_trans_id[0]:
            res.append(trans)
    return res

def build_plant_sup_trans_map(plant, sup):
    res=[]
    for i in range(0, len(plant.transitions)):
        res.append(get_associated_trans(i, sup))
    return res

def get_input_difference(sup_input_id, sup_input_weight, plant_trans):
    try:
        plant_input_index=plant_trans.input_ids.index(sup_input_id)
        plant_input_weight=plant_trans.input_weights[plant_input_index]
        return sup_input_weight - plant_input_weight
    except ValueError:
        return sup_input_weight

def build_modified_places_mapping(plant, sup, plant_sup_trans_map):
    res=[]
    for (plant_trans, sup_trans_list) in zip(plant.transitions, plant_sup_trans_map):
        weight_diff_vector=[]
        for sup_trans in sup_trans_list:
            trans_weight_diff_vector=[]
            for (input_id, input_weight) in zip(sup_trans.input_ids, sup_trans.input_weights):
                weight_diff=get_input_difference(input_id, input_weight, plant_trans)
                if weight_diff > 0:
                    trans_weight_diff_vector.append([input_id, input_weight, input_weight-weight_diff])
            weight_diff_vector.append(trans_weight_diff_vector)
        res.append(weight_diff_vector)
        
    return res

def build_pn_from_partial_cover_marking(partial_cover_marking, pn):
    res=copy.deepcopy(pn)
    res.n_places+=2
    res.place_names+=['ps', 'pf']
    ps_id=res.n_places-2
    pf_id=res.n_places-1
    res.initial_marking+=[1, 0]
    res.events+=['tf', 'place_consume']
    
    
    #build P\P^=
    p_geq=[]
    for i in range(0, res.n_places-2):
        if i not in partial_cover_marking.equal_place_ids:
            p_geq.append(i)
    
    #add self loops on ps
    for trans in res.transitions:
        trans.input_ids.append(ps_id)
        trans.output_ids.append(ps_id)
        trans.input_weights.append(1)
        trans.output_weights.append(1)
    
    #add t_f
    tf=EventTransition(input_ids=[ps_id],
        input_weights=[1],
        output_ids=[pf_id],
        output_weights=[1],
        event='tf')  
    for place in p_geq:
        n_tokens = partial_cover_marking.marking[place]
        if n_tokens > 0:
            tf.input_ids.append(place)
            tf.input_weights.append(n_tokens)
    for place in partial_cover_marking.equal_place_ids:
        if partial_cover_marking.marking[place] > 0:
            tf.input_ids.append(place)
            tf.input_weights.append(partial_cover_marking.marking[place])
            tf.output_ids.append(place)
            tf.output_weights.append(partial_cover_marking.marking[place])
    res.transitions.append(tf)
    
    for place in p_geq:
        tp=EventTransition(input_ids=[place, pf_id],
                           input_weights=[1, 1],
                           output_ids=[pf_id],
                           output_weights=[1],
                           event='place_consume')
        res.transitions.append(tp)
        
    reach_marking=[0 for i in range(0, res.n_places)]
    for place in partial_cover_marking.equal_place_ids:
        reach_marking[place]=partial_cover_marking.marking[place]
    reach_marking[pf_id]=1
    
    return (res, reach_marking)
    
    
    
    
    
    
                
                