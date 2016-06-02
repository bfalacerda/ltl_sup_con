from random import choice

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
    
    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.source==other.source and self.target==other.target and self.event==other.event
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)   
    
class DesAutomaton(object):
    def __init__(self,
                 initial_state,
                 accepting_states,
                 transitions,
                 events,
                 uc_events,
                 state_description_props,
                 product_automaton_labels=None):
        self.n_states=len(transitions)
        self.initial_state=initial_state
        self.accepting_states=accepting_states
        self.transitions=transitions
        self.events=events
        self.uc_events=uc_events
        self.state_description_props=state_description_props
        self.product_automaton_labels=product_automaton_labels
        
    def add_init_state(self):
        self.transitions.append([EventTransition(source=self.n_states,
                                                target=self.initial_state,
                                                event='init'
                                                )])
        self.events.append('init')
        self.state_description_props.append([])
        self.initial_state=self.n_states
        self.n_states+=1

        
    def __str__(self, print_trans=False):
        result="------DES model automaton info------\n"
        result+="States: " + str(self.n_states) + "\n"
        result+="Initial state: " + str(self.initial_state) + "\n"
        result+="Events: " + str(self.events) + "\n"
        result+="Uncontrollable events: " + str(self.uc_events) + "\n"
        result+="State description props: " + str(self.state_description_props) + "\n"
        result+="Transitions: \n"
        n_transitions=0   
        for source_state in self.transitions:
            for transition in source_state:
                if print_trans:
                    result+=str(transition)
                n_transitions+=1
        result+="Transitions: " + str(n_transitions) + "\n"
        if self.product_automaton_labels is not None:
            result+="\nProduct automaton labels: \n" + str(self.product_automaton_labels) + "\n"
        return result
    
    def print_dot(self):
        res='digraph G { \n rankdir=LR \n  node [shape="circle"] \n I [label="", style=invis, width=0] \n I -> '
        res+=str(self.initial_state) + "\n"
        for state in range(0,self.n_states):
            if self.product_automaton_labels is not None:
                res+=str(state) + ' [label = "' + str(state) + "\n" + str(self.product_automaton_labels[state]) + '\n' +  str(self.state_description_props[state]) + '"'
            else:
                res+=str(state) + ' [label = "' + str(state) + "\n" +  str(self.state_description_props[state]) + '"'
            if state in self.accepting_states:
                res+=', peripheries=2'
            res+=']\n'
            for transition in self.transitions[state]:
                res+=str(transition.source) + ' -> ' + str(transition.target) + ' [label="' + transition.event + '"]\n'
        res+='}'
        print(res)

    def random_run(self):
        state=self.initial_state
        while True:
            next_trans=choice(self.transitions[state])
            print(next_trans.event + '\n')
            state=next_trans.target
        
    def check_repeated_trans(self):
        n_trans=0
        total_trans=0
        for trans_list in self.transitions:
            total_trans=total_trans+len(trans_list)
            event_list =[trans.event for trans in trans_list]
            n_trans= n_trans + len(event_list) - len(set(event_list))
        return (n_trans, total_trans)

