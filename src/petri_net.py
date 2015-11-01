import des_dfa
from random import choice
from time import sleep
import copy
from subprocess import Popen, PIPE
import json

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
    
class PetriNet(object):
    #abstractPN:
    #self.read_pnml(file_name)
    #self.n_places=len(initial_marking)
    #self.initial_marking=initial_marking
    #self.transitions=transitions
    #self.events=events
    #self.uc_events=uc_events
    #self.state_description_props=state_description_props
    #self.true_state_places=true_state_places #{state_description_place:place_id,...}
    #self.false_state_places=false_state_places
    #self.place_names=[]

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
        self.events = list(self.events)
        self.events.append('init')
        self.initial_marking=[0 for i in range(0,self.n_places)]
        self.initial_marking.append(1)
        self.n_places+=1


    def generate_lola_byte_string(self):
        print("START WRITING LOLA")
        result="PLACE\n\nSAFE 1:\n"
        for i in range(0,self.n_places):
            result+="p" + str(i) + ', '
        result=result[:-2] + ";\n\nMARKING\n"
        for i in range(0,self.n_places):
            result+="\tp" + str(i) + (' : ') + str(self.initial_marking[i]) + ",\n"
        result=result[:-2] + ";\n\n"
        for i in range(0,len(self.transitions)):
            transition=self.transitions[i]
            result+="TRANSITION t" + str(i) + ".[" + transition.event + "]\n\tCONSUME\n"
            for (place_id, weight) in zip(transition.input_ids, transition.input_weights):
                result+="\t\tp" + str(place_id) + " : " + str(weight) + ",\n"
            result=result[:-2] + ";\n\tPRODUCE\n"
            for (place_id, weight) in zip(transition.output_ids, transition.output_weights):
                result+="\t\tp" + str(place_id) + " : " + str(weight) + ",\n"
            result=result[:-2] + ";\n"
        return result.encode('utf-8')
    
    def remove_dead_trans_lola(self):
        i=0
        j=0
        n_removed=0
        lola_model=self.generate_lola_byte_string()
        while i < len(self.transitions):
            transition=self.transitions[i]
            lola = Popen(["lola", "--formula=AG NOT FIREABLE(t" +  str(j) + ".[" + transition.event + "])", '--quiet',
                          "--json"], stdin=PIPE, stdout=PIPE)     
            output=lola.communicate(input=lola_model)
            result=json.loads(output[0].decode())
            result=result['analysis']['result']
            j+=1
            if result:
                print("dead")
                n_removed+=1
                del(self.transitions[i])
                print("REMOVE" + str(i/len(self.transitions)))
            else:
                print("live")
                i=i+1
            if n_removed%10 == 0:
                print("REGENERATING MODEL")
                j=i
                lola_model=self.generate_lola_byte_string()

    
    
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

    def random_run(self, sleep_time):
        marking=self.initial_marking
        while True:
            active_trans=self.get_active_transitions(marking)
            next_trans=choice(active_trans)
            print([str(trans) for trans in active_trans])
            print(next_trans.event + '\n')
            marking=self.fire_transition(marking,next_trans)
            sleep(sleep_time)

