# The LTL Supervisory Control Framework

A framework for building deterministic finite automata (DFA) and Petri net (PN) supervisors from safe LTL state/event specifications. It provides approaches for 3 different models:

1. DFA models. This is based on the work:

	Bruno Lacerda and Pedro U. Lima. [*LTL Plan Specification for Robotic Tasks Modelled as Finite State Automata*](http://www.cs.bham.ac.uk/~lacerdab/papers/LacerdaLima_ADAPT-AAMAS09Wks-cameraready.pdf). In Proceedings of the AAMAS '09 Workshop on Agent Design: Advancing from Practice to Theory (ADAPT), Budapest, Hungary, 2009

2. PN models with "symbolic" LTL semantics. In this case the truth value of certain atomic propositions is mapped into the presence of a token on a certain 1-bounded place in the PN. This is based on the work:

	Bruno Lacerda and Pedro U. Lima. [*Designing Petri Net Supervisors from LTL Specifications*](http://www.roboticsproceedings.org/rss07/p24.html). In Proceedings of the 2011 Robotics: Science and Systems Conference (RSS), Los Angeles, CA, USA, 2011

3. PN models where atomic propositions represent occurrence of events and linear constraints on the markings of the PN. This is an extension of 2.. It is based on the work:
	
	Bruno Lacerda. [*Supervision of Discrete Event Systems Based on Temporal Logic Specifications.*](http://welcome.isr.tecnico.ulisboa.pt/publications/supervision-of-discrete-event-systems-based-on-temporal-logic-specifications/)  PhD Thesis, Instituto Superior T&eacute;cnico, 2013. 


## Installation

### Source

Simply clone this repository, and install the dependencies below.

### Dependencies

``ltl_sup_con`` is implemented in Python 3 and relies on  two external tools:

1. The [Spot](https://spot.lrde.epita.fr/) library for automata generation. In particular, the Python 3 bindings need to be included.
1. The [TINA](http://projects.laas.fr/tina/) toolbox for PN analysis. In particular we use it for efficient reachability graph generation




## Usage

The framework works similarly for the 3 models, one just need to choose the appropriate classes. The basic idea is to model the system as a DFA, or a PN, and then write a set of safe LTL specs the models should keep true during its execution. The framework will then build a supervisor realization (DFA or PN, depending on the original model) such that the specs are satisfied. 

### Specification Language

#### LTL DFA

The [`LtlDfa`](src/ltl_dfa.py#L21) class is used by all 3 modelling approaches. An `LtlDfa` instance represents a DFA for an input safe LTL formula. The formula is provided as a string following the [Spot representation](https://spot.lrde.epita.fr/concepts.html#ltl) of LTL. An example of such a string is, for example, 

``G ((battery_high1 && (going_to_reception_area0 || at_reception_area0 || going_to_reception_area1 || at_reception_area1)) -> (X (!stop_offering_to_play1)))``

### DES Models

#### DES DFA

The [`DesAutomaton`](src/des_dfa.py#L25) represents a DFA model of a system. An example of building such a structure can be found [here](examples/soccer/soccer_dfa.py#L14).



#### Petri nets

The [`PetriNet`](src/petri_net.py#L50) class is used to represent general Petri net models. It provides some general methods that work both for "symbolic" and "algebraic" PNs (see below). It should not be used for composition with LTL automata.

* [`read_pnml`](src/petri_net.py#L69) allows for reading a PNML model, as saved by the [PIPE](http://pipe2.sourceforge.net/) modelling tool. This facilitates the modelling process by allowing the use of a GUI.

* [`remove_dead_trans_tina`](src/petri_net.py#L194) uses the TINA tool to enumerate the dead transitions in a `PetriNet`, and removes them from the structure.

* [`build_reachability_dfa`](src/petri_net.py#L317) builds the `DesDfa` corresponding to the reachability graph of the `PetriNet`. 

##### "Symbolic" PNs

The [`SymbPetriNet`](src/symb_pn.py#L7) represents a PN where (state-based) atomic propositions are represented by the presence or absence of tokens in a given 1-safe place. This is done by extending the `PetriNet` class with the following attributes:

* `state_description_props` is the list of state atomic propositions. Safe LTL specs can be wirrten over the set of events of the PN plus the elements of this list.

* `true_state_places` is a dictionary of the form `{state_description_prop:place_id,...}`, i.e., keys are elements of `state_description_props` and values are the id of the place in the PN structure that represents `state_description_prop` being true.

* `false_state_places` is a dictionary of the form `{state_description_prop:place_id,...}`, i.e., keys are elements of `state_description_props` and values are the id of the place in the PN structure that represents `state_description_prop` being false.

An example of building a `SymbPetriNet` can be found [here](examples/soccer/soccer_symb_pn.py/#L16). 

##### "Algebraic" PNs

The [`AlgPetriNet`](src/algebraic_pn.py#L11) represents a PN where (state-based) atomic propositions are represented by linear constraints over sets of bounded places. This is done by extending the `PetriNet` class with the following attributes:

* `bounded_places_descriptors` is a list of names for the different pairs of bounded places in the model.

* `place_bounds` is a dictionary of the form `{bounded_place_descriptor:k,...}`, i.e., keys are elements of `bounded_place_descriptors`, and values are the bound for the corresponding places

* `positive_bounded_places` is a dictionary of the form `{bounded_place_descriptor:i,...}`, i.e., keys are elements of `bounded_place_descriptors`, and values are the index of the place bounded by `place_bounds[bounded_place_descriptor]`

* `complement_bounded_places` is a dictionary of the form `{bounded_place_descriptor:i,...}`, i.e., keys are elements of `bounded_place_descriptors`, and values are the index of the complement place of `positive_bounded_places[bounded_place_descriptor]`.  This dict does not need to be fully defined, ad the method [`complete_prop_description`](src/algebraic_pn.py#L69) will add the misisng complement places from elements of `positive_bounded_places`. Note that for all markings `M` and elements of `bounded_place_descriptors`, we require 

 ``M(positive_bounded_places[bounded_place_descriptor]) + M(complement_bounded_places[bounded_place_descriptor]) = place_bounds[bounded_place_descriptor]``


This class also allows for the addition of *counter places*, using the method [`add_counter_place`](src/algebraic_pn.py#L155). This method receives a dict `weight_dict` mapping place names to its weight, and adds a place `counter` to the PN such that, for all markings `M`:

``M(counter) = weight_dict[place_1]*M(place_1) + ... +  weight_dict[place_n]*M(place_n)``

An example of building an `AlgPetriNet` can be found [here](examples/task/task_assignment.py).

### Compositions functions

We have defined composition functions for [`DesDfa`](src/des_dfa_compositions), [`SymbPetriNet`](src/symb_pn_compositions), and [`AlgPetriNet`](src/alg_pn_compositions). These are:

* `parallel_composition`: Given two DES models, returns the DES model corresponding to the parallel composition of the two input models by synchronising shared events.

* `ltl_dfa_composition`: Given a DES model, and an `LtlDfa`, builds the DES model representing the restriction of the language of the DES model to the language that satisfies the safe LTL formula used to generate the `LtlDfa`.

Examples of usage of these composition functions can be found [here](examples).


### Admissibility Checking

The admissibility checking algorithm for Petri nets is implemented [here](src/pn_admis_check.py) an requires the installation of the [LoLa 2.0](http://service-technology.org/files/lola/) tool. It is based on the approach presented in

Bruno Lacerda and Pedro U. Lima. [*On the Notion of Uncontrollable Marking in Supervisory Control of Petri Nets.*](http://ieeexplore.ieee.org/xpls/abs_all.jsp?arnumber=6807731&tag=1) IEEE Transactions on Automatic Control, Vol. 59, No. 11, 2014.

 Unfortunately, it is very inefficient, and cannot be used except for very small models. We suggest the use of the specification language restriction presented in

Bruno Lacerda. [*Supervision of Discrete Event Systems Based on Temporal Logic Specifications.*](http://welcome.isr.tecnico.ulisboa.pt/publications/supervision-of-discrete-event-systems-based-on-temporal-logic-specifications/)  PhD Thesis, Instituto Superior T&eacute;cnico, 2013.

This restriction guarantees admissibility by construction.


