import spot

class DnfTransitionDef(object):
    def __init__(self, 
                source=None,
                target=None,
                #string_label='',
                atomic_propositions=set(),
                vector_dnf_label=[] #((a & b) | (!c & d)) -> [{'a':True, 'b':True},{'c':False, 'd':True}]
                ): 
        self.source=source
        self.target=target
        #self.string_label=string_label
        self.atomic_propositions=atomic_propositions
        self.vector_dnf_label=vector_dnf_label
        
    def __str__(self):
        return "---- Transition info ----\n source: " + str(self.source) + "\n target: " + str(self.target) + "\n atomic_propositions: " + str(self.atomic_propositions) + "\n DNF label: " + str(self.vector_dnf_label) + "\n"


class LtlDfa(object):
    def __init__(self, ltl_string, print_dot=True):
        opt=None
        #build hoa dfa string representation
        cout = spot.get_cout()
        e = spot.default_environment.instance()
        p = spot.empty_parse_error_list()
        debug_opt = False
        f = spot.parse_infix_psl(ltl_string, p, e, debug_opt)
        dict = spot.make_bdd_dict()
        print("GENERATE")
        a = spot.ltl_to_tgba_fm(f, dict)
        print(a.to_str('hoa', opt))
        print("ENSURE")
        a = spot.ensure_digraph(a)
        print(a.to_str('hoa', opt))
        print("MINIMIZE")
        a = spot.minimize_obligation(a, f)
        print(a.to_str('hoa', opt))
        #a = degeneralized = spot.degeneralize(a)
        if print_dot:
            spot.print_dot(cout, a)
        
        hoa_string=a.to_str('hoa', opt)
        
        self.n_states=0
        self.initial_state=0
        self.accepting_states=[]
        self.transitions=[]
        self.atomic_propositions=[]
        
        hoa_string=hoa_string.split('\n')
        
        current_state=0
        i=0;
        line=None
        while line != '--END--':
            line=hoa_string[i]
            line=line.split(': ')
            if line[0]=='States':
                self.n_states=int(line[1])
                self.transitions=[[] for i in range(0,self.n_states)]
            elif line[0]=='Start':
                self.initial_state=int(line[1])
            elif line[0]=='AP':
                self.atomic_propositions=[i.strip('"') for i in line[1].split(' ')[1:]]
            elif line[0]=='State':
                line=line[1].split(' ')
                if current_state != int(line[0]):
                    print("ERROR")
                if '{' in line[-1]:
                    self.accepting_states.append(current_state)
                i+=1
                line=hoa_string[i]
                while 'State:' not in line:
                    if line == '--END--':
                        break
                    line=line.split(' ')
                    
                    transition=DnfTransitionDef(source=current_state,
                                                target=int(line[-1]),
                                                atomic_propositions=set(),
                                                vector_dnf_label=[]
                                                )
                    for conj_clause_string in line[:-1]:
                        conj_clause_rep={}
                        conj_clause_string=conj_clause_string.strip('[')
                        conj_clause_string=conj_clause_string.strip(']')
                        if conj_clause_string=='t':
                            transition.atomic_propositions=None
                            transition.vector_dnf_label=True
                            continue
                        if conj_clause_string == '|':
                            continue
                        conj_clause_string=conj_clause_string.split('&')
                        for literal_id in conj_clause_string:
                            if '!' in literal_id:
                                literal=self.atomic_propositions[int(literal_id[1:])]
                                transition.atomic_propositions.add(literal)
                                conj_clause_rep[literal]=False
                            else:
                                literal=self.atomic_propositions[int(literal_id)]
                                transition.atomic_propositions.add(literal)
                                conj_clause_rep[literal]=True
                        transition.vector_dnf_label.append(conj_clause_rep)                                                   
                    self.transitions[current_state].append(transition)
                    i+=1
                    line=hoa_string[i]
                current_state+=1
                continue
                    
            i+=1
        
    def __str__(self):
        result="------LTL DFA info------\n"
        result+="States: " + str(self.n_states) + "\n"
        result+="Initial state: " + str(self.initial_state) + "\n"
        result+="Accepting states: " + str(self.accepting_states) + "\n"
        result+="Atomic propositions: " + str(self.atomic_propositions) + "\n"
        result+="Transitions: \n"
        for source_state in self.transitions:
            for transition in source_state:
                result+=str(transition)
        return result
    
