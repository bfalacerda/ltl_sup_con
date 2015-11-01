from petri_net import PetriNet, EventTransition
import copy




class SymbPetriNet(PetriNet):    
    def __init__(self,
                 file_name='',
                 place_names=[],
                 initial_marking=[],
                 events=[],
                 uc_events=[],
                 transitions=[],
                 state_description_props=[],
                 true_state_places={},
                 false_state_places={}):
        if file_name != '':
            self.read_pnml(file_name)
        else:
            self.n_places=len(initial_marking)
            self.place_names=[]
            self.initial_marking=initial_marking
            self.transitions=transitions
            self.events=events
            self.uc_events=uc_events
            self.state_description_props=state_description_props
            self.true_state_places=true_state_places #{state_description_place:place_id,...}
            self.false_state_places=false_state_places
       
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
       
    def add_new_place_description(self, place_name):
        if place_name[0] =='!':
            if place_name[1:] not in self.state_description_props:
                self.state_description_props.append(place_name[1:])
            self.false_state_places[place_name[1:]]=self.n_places
        else:
            if place_name not in self.state_description_props:
                self.state_description_props.append(place_name)
            self.true_state_places[place_name]=self.n_places

    def complete_prop_description(self):
        for (true_prop, place_id) in self.true_state_places.items():
            if true_prop not in self.false_state_places:
                self.add_complement_place(place_id, true_prop, False)
        
        for (false_prop, place_id) in self.false_state_places.items():
            if false_prop not in self.true_state_places:
                self.add_complement_place(place_id, false_prop, True)
                
    def add_complement_place(self, original_place_id, prop_name, is_true_state_place):
        self.initial_marking.append((self.initial_marking[original_place_id]+1)%2)
        if is_true_state_place:
            self.place_names.append(self.place_names[original_place_id])
            self.true_state_places[prop_name]=self.n_places
        else:    
            self.place_names.append("!" + self.place_names[original_place_id])
            self.false_state_places[prop_name]=self.n_places
        for trans in self.transitions:
            is_input=(original_place_id in trans.input_ids)
            is_output=(original_place_id in trans.output_ids)
            if is_input and not is_output:
                trans.output_ids.append(self.n_places)
                trans.output_weights.append(1) #no caso geral tenho que procurar o input weight e fazer a conta
            if is_output and not is_input:
                trans.input_ids.append(self.n_places)
                trans.input_weights.append(1) #no caso geral tenho que procurar o output weight e fazer a conta
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
        self.n_places-=1
        for trans in self.transitions:
            for i in range(0, len(trans.input_ids)):
                if trans.input_ids[i]>init_place_id:
                    trans.input_ids[i]-=1
            for i in range(0, len(trans.output_ids)):
                if trans.output_ids[i]>init_place_id:
                    trans.output_ids[i]-=1
        for key in self.true_state_places:
            if self.true_state_places[key] > init_place_id:
                self.true_state_places[key]-=1
        for key in self.false_state_places:
            if self.false_state_places[key] > init_place_id:
                self.false_state_places[key]-=1


    def add_index(self, index):
        self.events=[event + str(index) for event in self.events]
        self.uc_events=[uc_event + str(index) for event in self.uc_events]
        for transition in self.transitions:
            transition.event=transition.event + str(index)
        self.state_description_props=[prop + str(index) for prop in self.state_description_props]
        self.true_state_places={key+str(index):value for (key,value) in self.true_state_places.items()}
        self.false_state_places={key+str(index):value for (key,value) in self.false_state_places.items()}
            
    

