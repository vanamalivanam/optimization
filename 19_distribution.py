#!/usr/bin/env python
from pyomo import environ as pe

from commons import output_to_display, run_solver

# liverpool and brighton
factories = ['li', 'br']
# new castle , birmingham, london, exetor
depots = 'nc bi lo ex'.split(' ')

cust = 'c1 c2 c3 c4 c5 c6'.split(' ')
prefs = {'c1': 'li', 'c2': 'nc', 'c5': 'bi', 'c6': ['ex', 'lo']}
fac_limit = {'li': 150, 'br': 200}
dep_limit = {'nc': 70, 'bi': 50, 'lo': 100, 'ex': 40}
c_req = {'c1': 50, 'c2': 10, 'c3': 40, 'c4': 35, 'c5': 60, 'c6': 20}
cmax = 10**7
# minimize overall cost
# from_to_table
"""
fd_cost = {}
fc_cost = {}
dc_cost = {}
from itertools import product

for f, d in product(factories, depots):
    fd_cost[(f, d)] = 0.0
for f, c in product(factories, cust):
    fc_cost[(f, c)] = 0.0
for d, c in product(depots, cust):
    dc_cost[(d, c)] = 0.0
"""

fd_cost = {('li', 'nc'): 0.5, ('li', 'bi'): 0.5, ('li', 'lo'): 1.0, ('li', 'ex'): 0.2,
           ('br', 'nc'): cmax, ('br', 'bi'): 0.3, ('br', 'lo'): 0.5, ('br', 'ex'): 0.2}

fc_cost = {('li', 'c1'): 1.0, ('li', 'c2'): cmax, ('li', 'c3'): 1.5, ('li', 'c4'): 2.0, ('li', 'c5'): cmax, ('li', 'c6'): 1.0,
           ('br', 'c1'): 2.0, ('br', 'c2'): cmax, ('br', 'c3'): cmax, ('br', 'c4'): cmax, ('br', 'c5'): cmax, ('br', 'c6'): cmax}

dc_cost = {('nc', 'c1'): cmax, ('nc', 'c2'): 1.5, ('nc', 'c3'): 0.5, ('nc', 'c4'): 1.5, ('nc', 'c5'): cmax, ('nc', 'c6'): 1.0,
           ('bi', 'c1'): 1.0, ('bi', 'c2'): 0.5, ('bi', 'c3'): 0.5, ('bi', 'c4'): 1.0, ('bi', 'c5'): 0.5, ('bi', 'c6'): cmax,
           ('lo', 'c1'): cmax, ('lo', 'c2'): 1.5, ('lo', 'c3'): 2.0, ('lo', 'c4'): cmax, ('lo', 'c5'): 0.5, ('lo', 'c6'): 1.5,
           ('ex', 'c1'): cmax, ('ex', 'c2'): cmax, ('ex', 'c3'): 0.2, ('ex', 'c4'): 1.5, ('ex', 'c5'): 0.5, ('ex', 'c6'): 1.5}

m = pe.ConcreteModel()
m.q_fd = pe.Var(fd_cost.keys(), within=pe.NonNegativeIntegers)
m.q_fc = pe.Var(fc_cost.keys(), within=pe.NonNegativeIntegers)
m.q_dc = pe.Var(dc_cost.keys(), within=pe.NonNegativeIntegers)
m.pref_sup = pe.ConstraintList()

# Factory manuf Capacities; two constraints
m.f_limit = pe.ConstraintList()
for f in factories:
    fcsub = filter(lambda t: t[0] == f, fc_cost)
    fdsub = filter(lambda t: t[0] == f, fd_cost)
    m.f_limit.add(sum(m.q_fc[i] for i in fcsub) + sum(m.q_fd[i] for i in fdsub) <= fac_limit[f])
# quantity into depots from factories with limit; 4 constraints
m.d_limit = pe.ConstraintList()
for d in depots:
    fdsub = filter(lambda t: t[1] == d, fd_cost)
    m.d_limit.add(sum(m.q_fd[i] for i in fdsub) <= dep_limit[d])

# Quantity out of Depots; two constraints
m.q_inout = pe.ConstraintList()
for d in depots:
    fdsub = filter(lambda t: t[1] == d, fd_cost)
    dcsub = filter(lambda t: t[0] == d, dc_cost)
    m.q_inout.add(sum(m.q_fd[i] for i in fdsub) - sum(m.q_dc[i] for i in dcsub) == 0)

# Customer Requirements; six constraints
m.tq = pe.ConstraintList()
for c in cust:
    fcids = filter(lambda t: t[1] == c, fc_cost)
    dcids = filter(lambda t: t[1] == c, dc_cost)
    m.tq.add(sum(m.q_fc[i] for i in fcids) + sum(m.q_dc[i] for i in dcids) == c_req[c])

# 198000 when this constraint is not added
"""
m.pref = pe.ConstraintList()
m.pref.add(m.q_fc[('li', 'c1')] == c_req['c1'])
m.pref.add(m.q_dc[('nc', 'c2')] == c_req['c2'])
m.pref.add(m.q_dc[('bi', 'c5')] == c_req['c5'])
m.pref.add(m.q_dc[('ex', 'c6')] + m.q_dc[('lo', 'c6')] == c_req['c6'])
"""


def _obj(m):
    expr = sum(m.q_fd[i] * fd_cost[i] for i in fd_cost.keys()) + \
        sum(m.q_fc[i] * fc_cost[i] for i in fc_cost.keys()) + \
        sum(m.q_dc[i] * dc_cost[i] for i in dc_cost.keys())
    return expr


m.objective = pe.Objective(rule=_obj, sense=pe.minimize)
results, log_fpath = run_solver(m, 'scip')
output_to_display(m, ['q_fc', 'q_dc', 'q_fd'])
