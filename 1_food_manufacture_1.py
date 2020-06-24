#!/usr/bin/env python
from commons import *
logging_level = 20

mod = pe.ConcreteModel()
oils = ['1', '2', '3', '4', '5']
vegoils = ['1', '2']
nvegoils = ['3', '4', '5']
months = ['jan', 'feb', 'march', 'april', 'may', 'june']
setattr(mod, 'buyq', pe.Var(months, oils, within=pe.NonNegativeReals, initialize=0))
setattr(mod, 'useq', pe.Var(months, oils, within=pe.NonNegativeReals, initialize=0))
setattr(mod, 'storeq', pe.Var(months, oils, within=pe.NonNegativeReals, initialize=0))

# In any month, it is not possible to refine more than 200 tons of vegetable oils and
# more than 250 tons of non-vegetable oils.
mod.voil_refine_limit_constr = pe.ConstraintList()
mod.nvoil_refine_limit_constr = pe.ConstraintList()
for m in months:
    mod.voil_refine_limit_constr.add(sum(mod.useq[m, o] for o in vegoils) <= 200)
    mod.voil_refine_limit_constr.add(sum(mod.useq[m, o] for o in nvegoils) <= 250)

# quantity of product generated one variable per month
mod.y = pe.Var(months, within=pe.NonNegativeReals, initialize=0)
# purchase cost of each month for oil1, oil2, oil3, oil4, oil5
futures = {'jan': [110, 120, 130, 110, 115], 'feb': [130, 130, 110, 90, 115],
           'march': [110, 140, 130, 100, 95], 'april': [120, 110, 120, 120, 125],
           'may': [100, 120, 150, 110, 105], 'june': [90, 100, 140, 80, 135]}

# profit for jan
# pa = 150*ya −110*b1a − 120*b2a − 130*b3a − 110*b4a − 115*b5a - 5*(s1a+s2a+s3a+s4a+s5a)
# profit for feb
# pb = −130*b1b − 130*b2b − 110*b3b − 90*b4b − 115*b5b + 150*yb - 5*(s1b+s2b+s3b+s4b+s5b)
# profit for march
# pc = −110*b1c − 140*b2c − 130*b3c − 100*b4c − 95*b5c + 150*yc  - 5*(s1c+s2c+s3c+s4c+s5c)
# profit for april
# pd = −120*b1d − 110*b2d − 120*b3d − 120*b4d − 125*b5d + 150*yd - 5*(s1d+s2d+s3d+s4d+s5d)
# profit for may
# pe = −90*b1e − 100*b2e − 140*b3e − 80*b4e − 135*b5e + 150*ye - 5*(s1e+s2e+s3e+s4e+s5e)
# profit for june
# pf = −110*b1f − 120*b2f − 130*b3f − 110*b4f − 115*b5f + 150*yf

# Profit = selling_price - cost_price - storage_price

def objective_expr(mod):
    # let pa, pb, pc, pd, pe, pf be the profits earned for each month.
    # total_profit =  pa + pb + pc + pd + pe + pf
    # expr = mod.pa + mod.pb + mod.pc + mod.pd + mod.pe + mod.pf
    expr = 150 * sum(mod.y[m] for m in months) - 5 * sum(mod.storeq[m, o]
                                                         for o in oils for m in months) - sum(futures[m][enm] * mod.buyq[m, o]
                                                                                              for enm, o in enumerate(oils) for m in months)
    return expr
mod.objective = pe.Objective(rule=objective_expr, sense=pe.maximize)

# oil hardness constraint
densities = {'1': 8.8, '2': 6.1, '3': 2, '4': 4.2, '5': 5}
mod.hardness = pe.ConstraintList()
for m in months:
    mod.hardness.add(sum(densities[o] * mod.useq[m, o] for o in oils) - 3 * mod.y[m] >= 0)
    mod.hardness.add(sum(densities[o] * mod.useq[m, o] for o in oils) - 6 * mod.y[m] <= 0)

# storage limit of 1000 tonnes of each raw oil for use later. The cost
# of storage for vegetable and non-vegetable oil is £5 per ton per month.
# TODO WARNING this constraint is not present in gurobi solution
mod.storage_con = pe.ConstraintList()
for m in months:
    for o in oils:
        mod.storage_con.add(mod.storeq[m, o] - 1000 <= 0)

# volumes must equate for each month.
# u1a + u2a + u3a + u4a + u5a = ya
mod.mass_conv = pe.ConstraintList()
for m in months:
    mod.mass_conv.add(sum(mod.useq[m, o] for o in oils) - mod.y[m] == 0)

"""
# from explanation in the book for the month of jan
BVEG 11 − UVEG 11 − SVEG 11 = −500,
SVEG 11 + BVEG 12 − UVEG 12 − SVEG 12 = 0,
SVEG 12 + BVEG 13 − UVEG 13 − SVEG 13 = 0,
SVEG 13 + BVEG 14 − UVEG 14 − SVEG 14 = 0,
SVEG 14 + BVEG 15 − UVEG 15 − SVEG 15 = 0,
SVEG 15 + BVEG 16 − UVEG 16 = 500
"""
mod.tally = pe.ConstraintList()
for o in oils:
    mod.tally.add(mod.buyq['jan',o] + 500 - mod.useq['jan', o] - mod.storeq['jan', o] == 0)
    mod.tally.add(mod.storeq['jan', o] + mod.buyq['feb', o] - mod.useq['feb',o] - mod.storeq['feb',o]==0)
    mod.tally.add(mod.storeq['feb',o] + mod.buyq['march', o] - mod.useq['march',o] - mod.storeq['march',o] ==0)
    mod.tally.add(mod.storeq['march', o] + mod.buyq['april',o] - mod.useq['april', o] - mod.storeq['april', o] ==0)
    mod.tally.add(mod.storeq['april',o] + mod.buyq['may',o] - mod.useq['may',o] - mod.storeq['may',o]==0)
    mod.tally.add(mod.storeq['may',o] + mod.buyq['june',o] - mod.useq['june',o] == 500)

results, log_fpath = run_solver(mod, stype='gurobi')
if logging_level == 10:
    print_bad_constr(mod, log_fpath)

# correct objective value: 107843
# current objective value: 120342
