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

* `bounded_places_descriptors`

* `place_bounds`

* `positive_bounded_places`

* `complement_bounded_places`













