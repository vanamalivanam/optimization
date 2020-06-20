#!/usr/bin/env python
import pyomo.environ as pe

from commons import output_to_display, run_solver

years = ['y1', 'y2', 'y3', 'y4', 'y5']
mines = ['m1', 'm2', 'm3', 'm4']
royalties = {'m1': 5, 'm2': 4, 'm3': 4, 'm4': 5}
mod = pe.ConcreteModel()
# how many mines are open per year
# =1 if mine i is worked in year t; 0 if
mod.delta = pe.Var(mines, years, initialize=0, within=pe.Binary)
# = 1 if mine i is ‘open’ in year t (i.e. royalities are payable) ;  =0 otherwise
mod.gamma = pe.Var(mines, years, initialize=0, within=pe.Binary)

mod.x = pe.Var(mines, years, initialize=0, within=pe.NonNegativeReals)
mod.q = pe.Var(years, initialize=0, within=pe.NonNegativeReals)
mine_limit = {'m1': 2000000, 'm2': 2500000, 'm3': 1300000, 'm4': 3000000}
mine_qlty = {'m1': 1.0, 'm2': 0.7, 'm3': 1.5, 'm4': 0.5}
mod.qty_con = pe.ConstraintList()
for yr in years:
    for m in mines:
        mod.qty_con.add(mod.x[m, yr] <= mine_limit[m] * mod.delta[m, yr])
mod.limit4_con = pe.ConstraintList()
# maximum number of mines per year is 3.
for yr in years:
    mod.limit4_con.add(sum(mod.delta[m, yr] for m in mines) <= 3)
# delta_it - gamma_it <=0
mod.gamma_delta_con = pe.ConstraintList()
for yr in years:
    for m in mines:
        mod.gamma_delta_con.add(mod.delta[m, yr] - mod.gamma[m, yr] <= 0)
# gamma_it+1 - gamma_it <=0
mod.gamma_gamma_con = pe.ConstraintList()
for enm in range(len(years) - 1):
    for m in mines:
        mod.gamma_gamma_con.add(mod.gamma[m, years[enm + 1]] - mod.gamma[m, years[enm]] <= 0)

# ore quality constraint
ore_qlty = {'y1': 0.9, 'y2': 0.8, 'y3': 1.2, 'y4': 0.6, 'y5': 1.0}
mod.ore_qlty_con = pe.ConstraintList()
for y in years:
    mod.ore_qlty_con.add(sum(mine_qlty[m] * mod.x[m, y] for m in mines) == mod.q[y] * ore_qlty[y])

# weight equation sum(x_it) - q_t = 0
mod.wts_cons = pe.ConstraintList()
for yr in years:
    mod.wts_cons.add(sum(mod.x[m, y] for m in mines) - mod.q[y] == 0)

# royalty
R = {'m1': 5000000, 'm2': 4000000, 'm3': 4000000, 'm4': 5000000}


def rule_objective(mod):
    # sum(I_t*q_t) - sum(R_it* gamma_it)
    expr = sum(10 * (1 - 0.1 * e) * mod.q[y] for e, y in enumerate(years)) - sum(R[m]
                                                                                 * (1 - 0.1 * e) * mod.gamma[m, y] for e, y in enumerate(years) for m in mines)
    return expr


mod.objective = pe.Objective(rule=rule_objective, sense=pe.maximize)

results, log_fpath = run_solver(mod)
output_to_display(mod, ['x', 'q', 'delta', 'gamma'])
