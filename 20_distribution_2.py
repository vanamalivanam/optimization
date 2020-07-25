#!/usr/bin/env python
from pyomo import environ as pe

from commons import output_to_display, run_solver

# liverpool and brighton
factories = ['li', 'br']
# new castle , birmingham, london, exetor
depots = 'nc bi lo ex'.split(' ')

cust = 'c1 c2 c3 c4 c5 c6'.split(' ')
fac_limit = {'li': 150, 'br': 200}  # factory limit
dep_limit = {'nc': 70, 'bi': 50, 'lo': 100, 'ex': 40}  # depot limit
c_req = {'c1': 50, 'c2': 10, 'c3': 40, 'c4': 35, 'c5': 60, 'c6': 20}  # customer requirement
cmax = 10**7
# from_to_table
fd_cost = {('li', 'nc'): 0.5, ('li', 'bi'): 0.5, ('li', 'lo'): 1.0, ('li', 'ex'): 0.2, ('li', 'bl'): 0.6, ('li', 'nh'): 0.4,
           ('br', 'nc'): cmax, ('br', 'bi'): 0.3, ('br', 'lo'): 0.5, ('br', 'ex'): 0.2, ('br', 'bl'): 0.4, ('br', 'nh'): 0.3}

fc_cost = {('li', 'c1'): 1.0, ('li', 'c2'): cmax, ('li', 'c3'): 1.5, ('li', 'c4'): 2.0, ('li', 'c5'): cmax, ('li', 'c6'): 1.0,
           ('br', 'c1'): 2.0, ('br', 'c2'): cmax, ('br', 'c3'): cmax, ('br', 'c4'): cmax, ('br', 'c5'): cmax, ('br', 'c6'): cmax}

dc_cost = {('nc', 'c1'): cmax, ('nc', 'c2'): 1.5, ('nc', 'c3'): 0.5, ('nc', 'c4'): 1.5, ('nc', 'c5'): cmax, ('nc', 'c6'): 1.0,
           ('bi', 'c1'): 1.0, ('bi', 'c2'): 0.5, ('bi', 'c3'): 0.5, ('bi', 'c4'): 1.0, ('bi', 'c5'): 0.5, ('bi', 'c6'): cmax,
           ('lo', 'c1'): cmax, ('lo', 'c2'): 1.5, ('lo', 'c3'): 2.0, ('lo', 'c4'): cmax, ('lo', 'c5'): 0.5, ('lo', 'c6'): 1.5,
           ('ex', 'c1'): cmax, ('ex', 'c2'): cmax, ('ex', 'c3'): 0.2, ('ex', 'c4'): 1.5, ('ex', 'c5'): 0.5, ('ex', 'c6'): 1.5,
           ('bl', 'c1'): 1.2, ('bl', 'c2'): 0.6, ('bl', 'c3'): 0.5, ('bl', 'c4'): cmax, ('bl', 'c5'): 0.3, ('bl', 'c6'): 0.8,
           ('nh', 'c1'): cmax, ('nh', 'c2'): 0.4, ('nh', 'c3'): cmax, ('nh', 'c4'): 0.5, ('nh', 'c5'): 0.6, ('nh', 'c6'): 0.9}

m = pe.ConcreteModel()
m.q_fd = pe.Var(fd_cost.keys(), within=pe.NonNegativeIntegers)
m.q_fc = pe.Var(fc_cost.keys(), within=pe.NonNegativeIntegers)
m.q_dc = pe.Var(dc_cost.keys(), within=pe.NonNegativeIntegers)

# Factory manuf Capacities; two constraints
m.f_limit = pe.ConstraintList()
for f in factories:
    fcsub = filter(lambda t: t[0] == f, fc_cost)
    fdsub = filter(lambda t: t[0] == f, fd_cost)
    m.f_limit.add(sum(m.q_fc[i] for i in fcsub) + sum(m.q_fd[i] for i in fdsub) <= fac_limit[f])

# Customer Requirements; six constraints
m.tq = pe.ConstraintList()
for c in cust:
    fcids = filter(lambda t: t[1] == c, fc_cost)
    dcids = filter(lambda t: t[1] == c, dc_cost)
    m.tq.add(sum(m.q_fc[i] for i in fcids) + sum(m.q_dc[i] for i in dcids) == c_req[c])

# after expansion birmingham becomes 50+20
new_dep = {'bl': 30, 'nh': 25}
dep_limit.update(new_dep)
print(dep_limit.keys())
# raise SystemError
# ['nc', 'bi', 'lo', 'ex', 'bl', 'nh']
# should new depots be constructed: bristol and newhampshire
m.renov_bool = pe.Var(['bl', 'nh', 'bi', 'nc', 'ex'], within=pe.Binary)

# quantity into depots from factories with limit; 4 constraints
m.d_limit = pe.ConstraintList()
for d in dep_limit:
    fdsub = filter(lambda t: t[1] == d, fd_cost)
    if d in ['bl', 'nh', 'nc', 'ex']:
        m.d_limit.add(sum(m.q_fd[i] for i in fdsub) <= dep_limit[d] * m.renov_bool[d])
    elif d == 'bi':
        m.d_limit.add(sum(m.q_fd[i] for i in fdsub) - m.renov_bool[d] * 20 <= dep_limit[d])
    else:
        m.d_limit.add(sum(m.q_fd[i] for i in fdsub) <= dep_limit[d])

# Quantity out of Depots; six constraints
m.q_inout = pe.ConstraintList()
for d in depots:
    fdsub = filter(lambda t: t[1] == d, fd_cost)
    dcsub = filter(lambda t: t[0] == d, dc_cost)
    m.q_inout.add(sum(m.q_fd[i] for i in fdsub) - sum(m.q_dc[i] for i in dcsub) == 0)

# connecting boolean constraints of depots with the quantity influx.
m.bool_rel_con = pe.ConstraintList()
m.bool_rel_con.add(sum(m.renov_bool[d] for d in ['bl', 'nh', 'nc', 'ex']) <= 2)


def _obj(m):
    # expr is cost of delivery
    expr = sum(m.q_fd[i] * fd_cost[i] for i in fd_cost.keys()) + \
        sum(m.q_fc[i] * fc_cost[i] for i in fc_cost.keys()) + \
        sum(m.q_dc[i] * dc_cost[i] for i in dc_cost.keys())
    # expr2 cost of setting up new depots and removing old depots
    # subtracting savings. from removing some depots.
    # if exeter is retained bool=1 => then savings from that must be zero
    # if newcastle is retained bool=1 => then savings from that must be zero
    expr2 = 12 * m.renov_bool['bl'] + 4 * m.renov_bool['nh'] + 3 * m.renov_bool['bi'] \
        - 10 * (1 - m.renov_bool['nc']) - 5 * (1 - m.renov_bool['ex'])
    return expr + expr2


m.objective = pe.Objective(rule=_obj, sense=pe.minimize)
results, log_fpath = run_solver(m, 'scip')
# output_to_display(m, ['q_fc', 'q_dc', 'q_fd', 'renov_bool'])
output_to_display(m, ['renov_bool'])
