# -*- mode: python; coding: utf-8 -*-
# Copyright (C) 2009, 2010, 2012, 2014, 2015 Laboratoire de Recherche et
# Développement de l'Epita (LRDE).
# Copyright (C) 2003, 2004 Laboratoire d'Informatique de Paris 6 (LIP6),
# département Systèmes Répartis Coopératifs (SRC), Université Pierre
# et Marie Curie.
#
# This file is part of Spot, a model checking library.
#
# Spot is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# Spot is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
# or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public
# License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# This is a python translation of the ltl2tgba C++ test program.
# Compare with src/tgbatest/ltl2tgba.cc.

import sys
import spot
import buddy

from automaton import CoSafeLtlAutomaton

arg = sys.argv[1]
cout = spot.get_cout()
e = spot.default_environment.instance()
p = spot.empty_parse_error_list()
debug_opt = False

f = spot.parse_infix_psl(arg, p, e, debug_opt)

dict = spot.make_bdd_dict()


a = spot.ltl_to_tgba_fm(f, dict)
a = spot.ensure_digraph(a)
a = spot.minimize_obligation(a, f)
a = degeneralized = spot.degeneralize(a)

opt=None
CoSafeLtlAutomaton(a.to_str('hoa', opt))

spot.print_dot(cout, a)
#print('--------------------------')

#spot.print_hoa(cout, a)
#print('--------------------------')

#spot.print_lbtt(cout, a)
#print('--------------------------')




#a.get_dict().dump(cout)
#print('--------------------------')
#spot.print_lbtt(cout, a)
#print('--------------------------')


#print(a)

#teste_iter=a.succ_iter(a.get_init_state())

#teste_iter.first()
#while not teste_iter.done():
    #print(teste_iter.current_state())
    #print(dir(teste_iter.current_condition()))
    #print(teste_iter.current_condition().id)
    #teste_iter.next()
    #print('--------------------------')
    #print(buddy.bdd_printset(teste_iter.current_condition()))


##print(teste_iter.current_state())
##print(teste_iter.current_condition())
##teste_iter.next()
##print(teste_iter.current_state()) 
##print(teste_iter.current_condition())

