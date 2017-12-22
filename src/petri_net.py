import des_dfa
from random import choice
from time import sleep
import copy
from subprocess import Popen, PIPE
import json
import xml.etree.ElementTree as ET
import pulp
from scipy.optimize import linprog

def is_int(s): #NOTA: ISTO FOI PARA FAZER UMA BATOTA ACHO
    try:
        int(s)
        return True
    except ValueError:
        return False

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
        
    def __eq__(self, other):
        if isinstance(other, self.__class__):
            res=True
            res=res and self.input_ids==other.input_ids
            res=res and self.input_weights==other.input_weights
            res=res and self.output_ids==other.output_ids
            res=res and self.output_weights==other.output_weights
            res=res and self.event==other.event
            return res
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)    

    def __str__(self):
        return "input ids=" + str(self.input_ids) + ", input_weights=" + str(self.input_weights) + " output ids=" + str(self.output_ids) + ", output_weights=" + str(self.output_weights) + ", event=" + self.event + "\n"
    
class PetriNet(object):
    #abstractPN:
    #self.read_pnml(file_name)
    #self.place_names=[]
    #self.n_places=len(initial_marking)
    #self.initial_marking=initial_marking
    #self.transitions=transitions
    #self.events=events
    #self.uc_events=uc_events
    ###Symb:
    #self.state_description_props=state_description_props
    #self.true_state_places=true_state_places #{state_description_place:place_id,...}
    #self.false_state_places=false_state_places
    ###Alg:
    #self.bounded_places_descriptors=self.bounded_places_descriptors
    #self.place_bounds=place_bounds
    #self.positive_bounded_places=positive_bounded_places
    #self.complement_bounded_places=complement_bounded_places
    
    def read_pnml(self, file_name):
        tree = ET.parse(file_name)
        root = tree.getroot()
        self.n_places=0
        self.initial_marking=[]
        self.place_names=[]
        self.state_description_props=[]
        self.true_state_places={}
        self.false_state_places={}
        self.bounded_places_descriptors=[]
        self.place_bounds={}
        self.positive_bounded_places={}
        self.complement_bounded_places={}
        
        for place in root.iter("place"):
            self.initial_marking.append(int(place.find("initialMarking").find("value").text[-1:]))
            name=place.find("name").find("value").text
            self.place_names.append(name)
            self.place_bounds[name]=int(place.find("capacity").find("value").text)
            self.add_new_place_description(name)
            self.n_places=self.n_places+1
            
        self.transition_names=[]
        self.transitions=[]
        self.events=set()
        self.uc_events=[]
        for trans in root.iter("transition"):
            name=trans.find("name").find("value").text
            self.transition_names.append(name)
            if is_int(name[-1]):
                event=name[:-1]
            else:
                event=name
            self.transitions.append(EventTransition(input_ids=[],
                                                    input_weights=[],
                                                    output_ids=[],
                                                    output_weights=[],
                                                    event=event))
            self.events.add(event)
            
            
        for arc in root.iter("arc"):
            source=arc.attrib["source"]
            target=arc.attrib["target"]
            weight=int(arc.find("inscription").find("value").text[-1])
            try:
                source_id=self.place_names.index(source)
                target_id=self.transition_names.index(target)
                self.transitions[target_id].input_ids.append(source_id)
                self.transitions[target_id].input_weights.append(weight)
            except ValueError:
                source_id=self.transition_names.index(source)
                target_id=self.place_names.index(target)
                self.transitions[source_id].output_ids.append(target_id)
                self.transitions[source_id].output_weights.append(weight)
        #self.complete_prop_descrition()
        #self.add_init_state()
    

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
        self.place_names.append('init_place')


    def generate_lola_string(self, byte_string=True):
        #print("START WRITING LOLA")
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
        if byte_string:
            return result.encode('utf-8')
        else:
            return result
        
    def generate_tina_string(self):
        result="net supervisor\n"
        i=0
        for transition in self.transitions:
            result+="tr t_" + str(i) + '_'  + transition.event + " "
            for (place_id, weight) in zip(transition.input_ids, transition.input_weights):
                result+="p" + str(place_id) + "*" + str(weight) + " "               
            result+="-> "             
            for (place_id, weight) in zip(transition.output_ids, transition.output_weights):
                result+="p" + str(place_id) + "*" + str(weight) + " "
            result+="\n"
            i+=1
        i=0
        for n_tokens in self.initial_marking:
            result+="pl p" + str(i) + " (" + str(n_tokens) + ")\n"            
            i+=1
        return result
    
    def remove_dead_trans_tina(self):
        n_removed=0
        tina_string=self.generate_tina_string()
        tina_model_file=open("tina.net", 'w')
        tina_model_file.write(tina_string)
        tina_model_file.close()
        tina=Popen(["/home/bruno/ltl_sup_con/tina-3.4.2/bin/tina", "-C", "-q", "-stats",  "tina.net"], stdin=PIPE, stdout=PIPE)
        output=tina.communicate()[0].decode()
        print(output)
        output=output.split(' ')
        print("REMOVING")
        n_output=len(output)
        
        i=0
        while output[i] != 'dead':
            i+=1
        i+=1    
        while output[i] != 'dead':
            i+=1
        n_dead= int(output[i-1].split('\n')[1])
        i+=3
        while "t_" not in output[i]:
            i+=1
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        print(n_dead)
        print(output[i])
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        dead_trans_ids = [int(output[i+j].split('_')[1]) for j in range(0,n_dead)]
        dead_trans_ids.sort(reverse=True)
        for dead_trans_id in dead_trans_ids:
            del(self.transitions[dead_trans_id])
            if hasattr(self, 'prod_trans_ids'):
                del(self.prod_trans_ids[dead_trans_id])
                            
    
    def remove_dead_trans_lola(self):
        i=0
        j=0
        n_removed=0
        lola_model=self.generate_lola_string()
        while i < len(self.transitions):
            transition=self.transitions[i]
            lola = Popen(["lola", "--formula=AG NOT FIREABLE(t" +  str(j) + ".[" + transition.event + "])", '--quiet',
                          "--json"], stdin=PIPE, stdout=PIPE)     
            output=lola.communicate(input=lola_model)
            result=json.loads(output[0].decode())
            result=result['analysis']['result']
            j+=1
            if result:
                #print("dead")
                n_removed+=1
                del(self.transitions[i])
                if hasattr(self, 'prod_trans_ids'):
                    del(self.prod_trans_ids[i])
                print("REMOVE" + str(i/len(self.transitions)))
            else:
                #print("live")
                i=i+1
            if n_removed%100 == 0:
                print("REGENERATING MODEL")
                j=i
                lola_model=self.generate_lola_string()

    
    
    def build_dead_trans_lp(self, transition_id): #uses pulp; doesnt work
        analysed_transition=self.transitions[transition_id]
        n_transitions=len(self.transitions)
        self.firing_count_vector=[pulp.LpVariable("t"+str(i),0) for i in range(0, n_transitions)]
        weights=[[0 for i in range(0,n_transitions)] for j in range(0,self.n_places)]
        for i in range(0, n_transitions):
            trans=self.transitions[i]
            for (input_id, input_weight) in zip(trans.input_ids, trans.input_weights):
                weights[input_id][i]=-input_weight
            for (output_id, output_weight) in zip(trans.output_ids, trans.output_weights):
                weights[output_id][i]+=output_weight
        i = 0
        while i < n_transitions:
            analysed_trans_input_weights=[0 for i in range(0,self.n_places)]
            prob=pulp.LpProblem("prob", pulp.LpMinimize)
            analysed_transition=self.transitions[i]
            for (input_id, input_weight) in zip(analysed_transition.input_ids, analysed_transition.input_weights):
                analysed_trans_input_weights[input_id]=input_weight    
            for j in range(0,self.n_places):
                prob+=self.initial_marking[j]+pulp.lpDot(weights[j], self.firing_count_vector) >= analysed_trans_input_weights[j]
            try:
                status = prob.solve(pulp.GLPK(msg=0))
                print(str(status))
                i=i+1
            except Exception:
                status = prob.solve(pulp.GLPK(msg=0))
                print(str(status))
                i=i+1
    
    def build_dead_trans_lp2(self, transition_id): #uses scipy very slow and removes very little transitions
        analysed_transition=self.transitions[transition_id]
        n_transitions=len(self.transitions)
        weights=[[0 for i in range(0,n_transitions)] for j in range(0,self.n_places)]
        for i in range(0, n_transitions):
            trans=self.transitions[i]
            for (input_id, input_weight) in zip(trans.input_ids, trans.input_weights):
                weights[input_id][i]=input_weight
            for (output_id, output_weight) in zip(trans.output_ids, trans.output_weights):
                weights[output_id][i]-=output_weight
        i = 0
        n_removed=0
        #bounds=[ for i in range(0,n_transitions)]
        objective=[0 for i in range(0,n_transitions)]
        while i < len(self.transitions):
            analysed_trans_input_weights=[0 for k in range(0,self.n_places)]
            analysed_transition=self.transitions[i]
            for (input_id, input_weight) in zip(analysed_transition.input_ids, analysed_transition.input_weights):
                analysed_trans_input_weights[input_id]=input_weight    
            restrictions=[self.initial_marking[k]-analysed_trans_input_weights[k] for k in range(0, self.n_places)]
            res=linprog(objective, A_ub=weights, b_ub=restrictions, bounds=(0,None), options={"disp": False})          
            if res.success:
                i=i+1
            else:
                n_removed+=1
                del(self.transitions[i])
                print("REMOVE" + str(i/len(self.transitions)))
  
        print(str(n_removed))

   
    
    
    def build_reachability_dfa(self, add_description_props=False): 
        n_states=0
        initial_state=0
        product_labels=[]
        events=self.events
        queue=[self.initial_marking]
        state_description_props=[]
        transitions=[]
        
        while queue!=[]:
            new_transitions=[]
            marking=queue.pop(0)
            #print(str(marking))
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
                if transition.event =='tf':
                    print("AHAH")
                    print(next_marking)
            n_states+=1
            #if n_states > 200:
                #break
            if n_states%1000 == 0:    
                print(n_states)
            if add_description_props:
                state_description_props.append(self.get_marking_true_props(marking))
            transitions.append(new_transitions)
        
        if not add_description_props:
            state_description_props=[[] for i in range(0,n_states)]
        product_labels=state_description_props
        return des_dfa.DesAutomaton(initial_state=initial_state,
                        accepting_states=[],
                        transitions=transitions,
                        events=events,
                        uc_events=events,
                        state_description_props=state_description_props,
                        product_automaton_labels=product_labels)
        
    def get_marking_true_props(self, marking):
        true_props=[]
        for (key,value) in self.true_state_places.items():
            if marking[value]==1:
                true_props.append(key)
        return true_props
    
    
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
            for trans in active_trans:
                print(str(trans))
            print(next_trans.event + '\n')
            marking=self.fire_transition(marking,next_trans)
            print(str(marking))
            sleep(sleep_time)
            
    
    def user_run(self):
        marking=self.initial_marking
        while True:
            active_trans=self.get_active_transitions(marking)
            next_trans=choice(active_trans)
            for trans in active_trans:
                print(str(trans))
            next_trans_id=input("Trans number?")
            next_trans=active_trans[int(next_trans_id)]
            print(next_trans.event + '\n')
            marking=self.fire_transition(marking,next_trans)
            
            
    def print_equal_trans(self):
        res=0
        for i in range(0, len(self.transitions)):
            trans1=self.transitions[i]
            for j in range(0,len(self.transitions)):
                if i!=j:
                    if trans1 == self.transitions[j]:
                        print(str(i) + '-' + str(j))
                        res+=1
        return res
    
    def check_reachability(self, marking):
        marking_lola='('
        for (index, n_tokens) in zip(range(0,self.n_places), marking):
            marking_lola+= "p" + str(index) + " = " + str(n_tokens) + " AND "
        marking_lola=marking_lola[:-5] + ")"
        lola_model=self.generate_lola_string()
        lola = Popen(["lola", '--formula=EF ' + marking_lola, '--quiet',
                          "--json"], stdin=PIPE, stdout=PIPE) 
        output=lola.communicate(input=lola_model)
        result=json.loads(output[0].decode())
        print(str(result['analysis']['result']))



