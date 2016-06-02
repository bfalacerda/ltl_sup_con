import sys
import inspect
import os
sys.path.append(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))) + '/../../src') #TODO: aprender a fazer isto como deve ser
from copy import deepcopy
from ltl_dfa import LtlDfa
from petri_net import EventTransition
import algebraic_pn
import alg_pn_compositions
import pn_admis_check as pac


n_robots=1
n_tasks=2
max_tasks=[1,1]
system_loaded=2
many_inactive_robots=0

max_system_load=0
for i in max_tasks:
    max_system_load+=i



pn_list=[None for i in range(0,n_robots)]

for i in range(0,n_robots):
    initial_marking=[n_robots,0,0,0]
    place_names=["idle_robots", "helping_robot", "broken_robots", "dead_robots"]
    transitions=[]
    bounded_place_descriptors=["idle_robots", "helping_robot", "broken_robots", "dead_robots"]
    place_bounds={"idle_robots":n_robots, 
                  "helping_robot":n_robots,
                  "broken_robots":n_robots, 
                  "dead_robots":n_robots}
    positive_bounded_places={"idle_robots":0, 
                            "helping_robot":1,
                            "broken_robots":2, 
                            "dead_robots":3}
    complement_bounded_places={}

    events=['help_robot',
            'replace_robot',
            'robot_is_dead',
            'help_finished',
            'help_failed']
    uc_events=['robot_is_dead',
            'help_finished',
            'help_failed']
    transitions.append(EventTransition(input_ids=[0,2],
                                            input_weights=[1, 1],
                                            output_ids=[1],
                                            output_weights=[1],
                                            event='help_robot'))
    transitions.append(EventTransition(input_ids=[1],
                                            input_weights=[1],
                                            output_ids=[0],
                                            output_weights=[2],
                                            event='help_finished'))
    transitions.append(EventTransition(input_ids=[1],
                                            input_weights=[1],
                                            output_ids=[2],
                                            output_weights=[2],
                                            event='failed_helping'))

    transitions.append(EventTransition(input_ids=[1],
                                            input_weights=[1],
                                            output_ids=[0, 3],
                                            output_weights=[1, 1],
                                            event='dead_robot'))
    transitions.append(EventTransition(input_ids=[3],
                                            input_weights=[1],
                                            output_ids=[0],
                                            output_weights=[1],
                                            event='replace_robot'))
    transitions.append(EventTransition(input_ids=[2],
                                            input_weights=[n_robots],
                                            output_ids=[0],
                                            output_weights=[n_robots],
                                            event='restart_system'))
    

for i in range(0, n_tasks):
    initial_marking+=[0, max_tasks[i], 0, 0, 0]
    bounded_place_descriptors+=["tasks_in_system_" + str(i),
                                "queue_new_tasks_" + str(i),
                                "queue_failed_tasks_" + str(i),
                                "executing_task_" + str(i)]
    place_names+=["tasks_in_system_" + str(i),
                "!tasks_in_system_" + str(i),
                "queue_new_tasks_" + str(i),
                "queue_failed_tasks_" + str(i),
                "executing_task_" + str(i)]
        
        
    place_bounds["tasks_in_system_" + str(i)]=max_tasks[i]
    place_bounds["queue_new_tasks_" + str(i)]=max_tasks[i] 
    place_bounds["queue_failed_tasks_" + str(i)]=max_tasks[i] 
    place_bounds["executing_task_" + str(i)]=max_tasks[i] 
        
    index=4+i*5   
    positive_bounded_places["tasks_in_system_" + str(i)]=index
    positive_bounded_places["queue_new_tasks_" + str(i)]=index+2 
    positive_bounded_places["queue_failed_tasks_" + str(i)]=index+3
    positive_bounded_places["executing_task_" + str(i)]=index+4
    
    complement_bounded_places["tasks_in_system_" + str(i)]=index+1
    
    events+=["task_arrival_" + str(i),
            "assign_new_task_" + str(i),
            "assign_incomplete_task_" + str(i),
            "failed_task_" + str(i),
            "finished_task_" + str(i)]
    uc_events+=["task_arrival_" + str(i),
            "failed_task_" + str(i),
            "finished_task_" + str(i)]
    
    transitions.append(EventTransition(input_ids=[index+1],
                                        input_weights=[1],
                                        output_ids=[index, index+2],
                                        output_weights=[1, 1],
                                        event="task_arrival_" + str(i)))
    transitions.append(EventTransition(input_ids=[0, index+2],
                                        input_weights=[1, 1],
                                        output_ids=[index+4],
                                        output_weights=[1],
                                        event="assign_new_task_" + str(i)))
    transitions.append(EventTransition(input_ids=[0, index+3],
                                        input_weights=[1, 1],
                                        output_ids=[index+4],
                                        output_weights=[1],
                                        event="assign_incomplete_task_" + str(i)))
    transitions.append(EventTransition(input_ids=[index, index+4],
                                        input_weights=[1, 1],
                                        output_ids=[0, index+1],
                                        output_weights=[1, 1],
                                        event="finished_task_" + str(i)))
    transitions.append(EventTransition(input_ids=[index+4],
                                        input_weights=[1],
                                        output_ids=[2, index+3],
                                        output_weights=[1, 1],
                                        event="failed_task_" + str(i)))
            

pn=algebraic_pn.AlgPetriNet(place_names=place_names,
                            initial_marking=initial_marking,
                            events=events,
                            uc_events=uc_events,
                            transitions=transitions,
                            bounded_places_descriptors=bounded_place_descriptors,
                            place_bounds=place_bounds,
                            positive_bounded_places=positive_bounded_places,
                            complement_bounded_places=complement_bounded_places,
                            prod_trans_ids=[])
pn.complete_prop_description()
    
#pn.random_run(0.5)

counter_place_def={}
for i in range(0, n_tasks):
    counter_place_def['tasks_in_system_' + str(i)]=1
pn.add_counter_place(counter_place_def, "system_load_counter")

counter_place_def={}
for i in range(0, n_tasks):
    counter_place_def['queue_failed_tasks_' + str(i)]=1
pn.add_counter_place(counter_place_def, "failed_tasks_counter")

counter_place_def={'queue_new_tasks_0':1, '!queue_new_tasks_1':1}
pn.add_counter_place(counter_place_def, "task_diff01")

counter_place_def={'!queue_new_tasks_0':1, 'queue_new_tasks_1':1}
pn.add_counter_place(counter_place_def, "task_diff10")

counter_place_def={'broken_robots':1, 'dead_robots':1}
pn.add_counter_place(counter_place_def, "inactive_robots")

pn.add_init_state()

if True:

    formulas_list=[None for i in range(0, 5)]
    spgecs_list=[None for i in range(0, 5)]



    formulas_list[0]='[] (( !system_loaded) -> (X (!replace_robot)))'
    spgecs_list[0]={'system_loaded':['system_load_counter',system_loaded], '!system_loaded':['!system_load_counter',max_system_load-system_loaded+1]}

    formulas_list[1]='[] ((many_inactive_robots) -> (X ('
    spgecs_list[1]={'many_inactive_robots':['inactive_robots',many_inactive_robots], '!many_inactive_robots':['!inactive_robots',n_robots-many_inactive_robots+1]}

    formulas_list[2]='[] ((waiting_failed_tasks) -> (X ('
    spgecs_list[2]={'waiting_failed_tasks':['failed_tasks_counter', 1], '!waiting_failed_tasks':['!failed_tasks_counter',max_system_load]}

    formulas_list[3]='[] ((more_1_than_0 & !two_or_more_new_tasks_0) -> (X ( !assign_new_task_0)))'
    spgecs_list[3]={'more_1_than_0':['task_diff10', max_tasks[1] + 1], '!more_1_than_0':['!task_diff10',max_tasks[0]], 
                    'two_or_more_new_tasks_0':['queue_new_tasks_0',2], '!two_or_more_new_tasks_0':['!queue_new_tasks_0', max_tasks[0]-1]}

    formulas_list[4]='[] ((less_eq_1_than_0 | three_or_more_new_tasks_0) -> (X ( !assign_new_task_1)))'
    spgecs_list[4]={'less_eq_1_than_0':['task_diff01', max_tasks[0]], '!less_eq_1_than_0':['!task_diff01', max_tasks[1]+1], 
                    'three_or_more_new_tasks_0':['queue_new_tasks_0',3], '!three_or_more_new_tasks_0':['!queue_new_tasks_0', max_tasks[0]-2]}

    for i in range(0, n_tasks):
        formulas_list[1]+='!assign_new_task_' + str(i) + ' & !assign_incomplete_task_' + str(i) + ' & '
        formulas_list[2]+='!assign_new_task_' + str(i) + ' & '

    formulas_list[1]=formulas_list[1][:-3] + ')))'
    formulas_list[2]=formulas_list[2][:-3] + ')))'





    res=pn
    n_specs=0
    i=0
    for (formula, spgec_def) in zip(formulas_list, spgecs_list):
        if True:
            print(formula)
            ltl_dfa=LtlDfa(formula)
            print(spgec_def)
            res=alg_pn_compositions.alg_pn_ltl_dfa_composition(res,ltl_dfa,spgec_def,n_specs)
            print("--------------------------\n\n\n")
            #print(res)
            print(res.n_places)
            print(len(res.transitions))
            n_specs+=1
        i+=1
    #res.remove_dead_trans_tina()


    formula='(' + formulas_list[0] + ') & (' + formulas_list[1] +  ') & (' + formulas_list[2] +  ') & (' + formulas_list[3] + ') & (' + formulas_list[4] + ')'
    #formula='(' + formulas_list[3] +  ') & (' + formulas_list[4] + ')'
    spgecs=deepcopy(spgecs_list[0])
    spgecs.update(spgecs_list[1])
    spgecs.update(spgecs_list[2])
    spgecs.update(spgecs_list[3])
    spgecs.update(spgecs_list[4])
    res2=pn
    ltl_dfa=LtlDfa(formula)
    res2=alg_pn_compositions.alg_pn_ltl_dfa_composition(res2,ltl_dfa,spgecs,0)
    
    
    
print("_______________________________________________")
print("incremental  places: " + str(res.n_places))
print("incremental trans: " + str(len(res.transitions)))

print("_______________________________________________")
print("conjunction places: " + str(res2.n_places))
print("conjunction trans: " + str(len(res2.transitions)))

res.remove_dead_trans_tina()
res2.remove_dead_trans_tina()

if True:
    plant_sup_trans_map=pac.build_plant_sup_trans_map(pn, res2)
    mod_places_mapping=pac.build_modified_places_mapping(pn, res2, plant_sup_trans_map)
    input_place_combs=pac.InputPlaceCombs(mod_places_mapping)
    for (trans, places_list, ks_list) in zip(pn.transitions, input_place_combs.place_ids, input_place_combs.all_ks):
        if trans.event in uc_events:
            for (place_ids, k_tuples) in zip(places_list, ks_list):
                for k_tuple in k_tuples:
                    pcm=pac.PartialCoveringMarking(trans, res2.n_places, place_ids, k_tuple)
                    (new_pn, reach_marking) = pac.build_pn_from_partial_cover_marking(pcm, res2)
                    print("CHECKING")
                    new_pn.check_reachability(reach_marking)
                    
            




