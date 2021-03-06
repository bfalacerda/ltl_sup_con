from petri_net import PetriNet, EventTransition
import copy

def weight_dict_to_str(weight_dict):
    res='('
    for (key, value) in weight_dict.items():
        res+= 'M(' + key + ')>=' + str(value) + ' && '
    res=res[:-4] + ')'
    return res

class AlgPetriNet(PetriNet):    
    def __init__(self,
                 file_name='',
                 place_names=[],
                 initial_marking=[],
                 events=[],
                 uc_events=[],
                 transitions=[],
                 bounded_places_descriptors=[],
                 place_bounds={},
                 positive_bounded_places={},
                 complement_bounded_places={},
                 prod_trans_ids=[]):
        self.prod_trans_ids=prod_trans_ids
        if file_name != '':
            self.read_pnml(file_name)
        else:
            self.n_places=len(initial_marking)
            self.place_names=place_names
            self.initial_marking=initial_marking
            self.transitions=transitions
            self.events=events
            self.uc_events=uc_events
            self.bounded_places_descriptors=bounded_places_descriptors
            self.place_bounds=place_bounds
            self.positive_bounded_places=positive_bounded_places
            self.complement_bounded_places=complement_bounded_places
            
       
    def __str__(self, print_trans=True):
        result="------Algebraic PN model info------\n"
        result+="Places: " + str(self.n_places) + "\n"
        result+="Initial marking: " + str(self.initial_marking) + "\n"
        result+="Events: " + str(self.events) + "\n"
        result+="Uncontrollable events: " + str(self.uc_events) + "\n"
        result+="Transitions: \n"
        n_transitions=0   
        for transition in self.transitions:
                if print_trans:
                    result+=str(transition)
                n_transitions+=1
        result+="Transitions: " + str(n_transitions) + "\n"
        result+="Place bounds:" + str(self.place_bounds) + "\n"
        result+="Positive bounded places:" + str(self.positive_bounded_places) + "\n"
        result+="Complement bounded places:" + str(self.complement_bounded_places) + "\n"
        return result
       
    def add_new_place_description(self, place_name):
        if place_name[0] =='!':
            if place_name[1:] not in self.state_description_props:
                self.bounded_places_descriptors.append(place_name[1:])
            self.complement_bounded_places[place_name[1:]]=self.n_places
        else:
            if place_name not in self.state_description_props:
                self.bounded_places_descriptors.append(place_name)
            self.positive_bounded_places[place_name]=self.n_places
        

    def complete_prop_description(self):
        for (descriptor, place_id) in self.positive_bounded_places.items():
            if descriptor not in self.complement_bounded_places:
                self.add_complement_place(place_id, descriptor, False)
        
        for (descriptor, place_id) in self.complement_bounded_places.items():
            if descriptor not in self.positive_bounded_places:
                self.add_complement_place(place_id, descriptor, True)
                
    def add_complement_place(self, original_place_id, descriptor, is_positive):
        bound=self.place_bounds[self.place_names[original_place_id]]
        self.initial_marking.append(bound - self.initial_marking[original_place_id])
        if is_positive:
            name=self.place_names[original_place_id]
            self.place_names.append(name)
            self.positive_bounded_places[descriptor]=self.n_places
            self.place_bounds[name]=bound
        else:    
            name="!" + self.place_names[original_place_id]
            self.place_names.append(name)
            self.complement_bounded_places[descriptor]=self.n_places
            self.place_bounds[name]=bound
        for trans in self.transitions:
            is_input=(original_place_id in trans.input_ids)
            is_output=(original_place_id in trans.output_ids)
            if is_input and not is_output:
                trans.output_ids.append(self.n_places)
                trans.output_weights.append(trans.input_weights[trans.input_ids.index(original_place_id)])
            if is_output and not is_input:
                trans.input_ids.append(self.n_places)
                trans.input_weights.append(trans.output_weights[trans.output_ids.index(original_place_id)])
            if is_input and is_output:
                input_weight=trans.input_weights[trans.input_ids.index(original_place_id)]
                output_weight=trans.output_weights[trans.output_ids.index(original_place_id)]
                if input_weight>output_weight:
                    trans.output_ids.append(self.n_places)
                    trans.output_weights.append(input_weight-output_weight)
                elif output_weight>input_weight:
                    trans.input_ids.append(self.n_places)
                    trans.output_weights.append(output_weight-input_weight)
        self.n_places+=1
        

    def remove_init_state(self):
        self.events=list(self.events)
        del self.events[self.events.index('init')]
        for i in range(0,len(self.transitions)):
            trans=self.transitions[i]
            if trans.event=='init':
                init_place_id=trans.input_ids[0]
                initial_marking_places=trans.output_ids
                initial_marking_values=trans.output_weights
                del self.transitions[i]
                break
        for (place_id, weight) in zip(initial_marking_places, initial_marking_values):
            self.initial_marking[place_id]=weight
        del self.initial_marking[init_place_id]
        del self.place_names[init_place_id]
        self.n_places-=1
        for trans in self.transitions:
            for i in range(0, len(trans.input_ids)):
                if trans.input_ids[i]>init_place_id:
                    trans.input_ids[i]-=1
            for i in range(0, len(trans.output_ids)):
                if trans.output_ids[i]>init_place_id:
                    trans.output_ids[i]-=1
        for (key, value) in self.positive_bounded_places.items():
            if value > init_place_id:
                self.positive_bounded_places[key]=value-1
        for (key, value) in self.complement_bounded_places.items():
            if value > init_place_id:
                self.complement_bounded_places[key]=value-1
        


    def add_index(self, index):
        self.place_names=[name + str(index) for name in self.place_names]
        self.events=[event + str(index) for event in self.events]
        self.uc_events=[uc_event + str(index) for uc_event in self.uc_events]
        for transition in self.transitions:
            transition.event=transition.event + str(index)
        self.bounded_places_descriptors=[prop + str(index) for prop in self.bounded_places_descriptors]
        self.place_bounds={key+str(index):value for (key,value) in self.place_bounds.items()}
        self.positive_bounded_places={key+str(index):value for (key,value) in self.positive_bounded_places.items()}
        self.complement_bounded_places={key+str(index):value for (key,value) in self.complement_bounded_places.items()}
        
    def add_counter_place(self, weight_dict, counter_place_name=None):
        for trans in self.transitions:
            weight=0
            for (input_id, input_weight) in zip(trans.input_ids, trans.input_weights):
                name=self.place_names[input_id]
                if name in weight_dict:
                    weight=weight - weight_dict[name]*input_weight
            for (output_id, output_weight) in zip(trans.output_ids, trans.output_weights):
                name=self.place_names[output_id]
                if name in weight_dict:
                    weight=weight + weight_dict[name]*output_weight
            if weight<0:
                trans.input_ids.append(self.n_places)
                trans.input_weights.append(-weight)
            elif weight>0:
                trans.output_ids.append(self.n_places)
                trans.output_weights.append(weight)
        initial_marking=0
        bound=0
        for (key,value) in weight_dict.items():
            index=self.place_names.index(key)
            initial_marking+=value*self.initial_marking[index]
            if key[0]=='!':
                bound+=value*self.place_bounds[key[1:]]
            else:
                bound+=value*self.place_bounds[key]
        self.initial_marking.append(initial_marking)
        if counter_place_name is None:
            counter_place_name = weight_dict_to_str(weight_dict)
        self.place_names.append(counter_place_name)
        self.bounded_places_descriptors.append(counter_place_name)
        self.positive_bounded_places[counter_place_name]=self.n_places
        self.place_bounds[counter_place_name]=bound      
        self.n_places+=1
        self.add_complement_place(self.n_places-1, counter_place_name, False)
        
       
