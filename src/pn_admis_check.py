from petri_net import EventTransition, PetriNet
from symb_pn import SymbPetriNet
import copy

def get_associated_trans(plant_trans_id, sup):
    res=[]
    for (trans, original_trans_id) in zip(sup.transitions, sup.prod_trans_ids):
        if plant_trans_id == original_trans_id[0]:
            res.append(trans)
    return res

