# 12.2 Food manufacture 2
#!/usr/bin/env python
#!/usr/bin/env python
import numpy as np
import pandas as pd

from commons import *

logging_level = 20

mod = pe.ConcreteModel()
oils = ['1', '2', '3', '4', '5']
vegoils = ['1', '2']
nvegoils = ['3', '4', '5']
months = ['jan', 'feb', 'march', 'april', 'may', 'june']
# purchase cost of each month for oil1, oil2, oil3, oil4, oil5
futures = {'jan': [110, 120, 130, 110, 115], 'feb': [130, 130, 110, 90, 115],
           'march': [110, 140, 130, 100, 95], 'april': [120, 110, 120, 120, 125],
           'may': [100, 120, 150, 110, 105], 'june': [90, 100, 140, 80, 135]}
# quantity of product generated one variable per month
mod.y = pe.Var(months, within=pe.NonNegativeReals, initialize=0)
mod.buyq = pe.Var(months, oils, within=pe.NonNegativeReals, initialize=0)
mod.useq = pe.Var(months, oils, within=pe.NonNegativeReals, initialize=0)
mod.storeq = pe.Var(months, oils, within=pe.NonNegativeReals, initialize=0)

# jupyter cell 4 and 5
"""
# from explanation in the book for one oil
500   + BVEG1 − UVEG1 − SVEG1 = 0,
SVEG1 + BVEG2 − UVEG2 − SVEG2 = 0,
SVEG2 + BVEG3 − UVEG3 − SVEG3 = 0,
SVEG3 + BVEG4 − UVEG4 − SVEG4 = 0,
SVEG4 + BVEG5 − UVEG5 − SVEG5 = 0,
SVEG5 + BVEG6 − UVEG6 = 500
"""
mod.tally = pe.ConstraintList()
for o in oils:
    mod.tally.add(500                  + mod.buyq['jan', o] - mod.useq['jan', o] - mod.storeq['jan', o] == 0)
    mod.tally.add(mod.storeq['jan', o] + mod.buyq['feb', o] - mod.useq['feb', o] - mod.storeq['feb', o] == 0)
    mod.tally.add(mod.storeq['feb', o] + mod.buyq['march', o] - mod.useq['march', o] - mod.storeq['march', o] == 0)
    mod.tally.add(mod.storeq['march', o] + mod.buyq['april', o] - mod.useq['april', o] - mod.storeq['april', o] == 0)
    mod.tally.add(mod.storeq['april', o] + mod.buyq['may', o] - mod.useq['may', o] - mod.storeq['may', o] == 0)
    mod.tally.add(mod.storeq['may', o] + mod.buyq['june', o] - mod.useq['june', o] - mod.storeq['june', o] == 0)
    mod.tally.add(mod.storeq['june', o] == 500)
# In any month, it is not possible to refine more than 200 tons of vegetable oils and
# more than 250 tons of non-vegetable oils.
# jupyter cell 6
mod.voil_refine_limit_constr = pe.ConstraintList()
mod.nvoil_refine_limit_constr = pe.ConstraintList()
for m in months:
    mod.voil_refine_limit_constr.add(sum(mod.useq[m, o] for o in vegoils) <= 200)
    mod.voil_refine_limit_constr.add(sum(mod.useq[m, o] for o in nvegoils) <= 250)

# oil hardness constraint; jupyter cell 7
densities = {'1': 8.8, '2': 6.1, '3': 2.0, '4': 4.2, '5': 5.0}
mod.hardness = pe.ConstraintList()
for m in months:
    mod.hardness.add(sum(densities[o] * mod.useq[m, o] for o in oils) - 3 * mod.y[m] >= 0)
    mod.hardness.add(sum(densities[o] * mod.useq[m, o] for o in oils) - 6 * mod.y[m] <= 0)

# jupyter cell 8
# volumes must equate for each month.
# u1a + u2a + u3a + u4a + u5a = ya
mod.mass_conv = pe.ConstraintList()
for m in months:
    mod.mass_conv.add(sum(mod.useq[m, o] for o in oils) - mod.y[m] == 0)

def objective_expr(mod):
    # let pa, pb, pc, pd, pe, pf be the profits earned for each month.
    # total_profit =  pa + pb + pc + pd + pe + pf
    # expr = mod.pa + mod.pb + mod.pc + mod.pd + mod.pe + mod.pf
    expr = sum(150 * mod.y[m] - 5 * sum(mod.storeq[m, o] for o in oils) - sum(futures[m][enm] * mod.buyq[m, o]
                                                                              for enm, o in enumerate(oils)) for m in months)
    return expr


mod.objective = pe.Objective(rule=objective_expr, sense=pe.maximize)
# storage limit of 1000 tonnes of each raw oil for use later. The cost
# of storage for vegetable and non-vegetable oil is £5 per ton per month.
# this constraint has no effect on the objective value.
mod.storage_con = pe.ConstraintList()
for m in months:
    for o in oils:
        mod.storage_con.add(mod.storeq[m, o] - 1000 <= 0)

################################################################################
# problem 2:
"""It is wished to impose the following extra conditions on the food manufacture problem:"""
boolkeys = []
mod.bool_useq = pe.Var(months, oils, within=pe.Binary, initialize=0)
"""1. If an oil is used in a month, at least 20 tons must be used."""
mod.minmax = pe.ConstraintList()
l = 20
max_cap = {'1': 200, '2': 200, '3': 250, '4': 250, '5': 250}
for m in months:
    for o in oils:
        x = max_cap[o]
        mod.minmax.add(mod.useq[m, o] - x * mod.bool_useq[m, o] <= 0)
        mod.minmax.add(mod.useq[m, o] - l * mod.bool_useq[m, o] >= 0)

"""2. If either of VEG 1 or VEG 2 are used in a month then OIL 3 must also be used."""
mod.eitheror = pe.ConstraintList()
for m in months:
    mod.eitheror.add(mod.bool_useq[m, '1'] - mod.bool_useq[m, '5'] <= 0)
    mod.eitheror.add(mod.bool_useq[m, '2'] - mod.bool_useq[m, '5'] <= 0)

"""3. The food may never be made up of more than three oils in any month."""
mod.three_oil = pe.ConstraintList()
for m in months:
    mod.three_oil.add(sum(mod.bool_useq[m, o] for o in oils) <= 3)

# solve the optimization problem
results, log_fpath = run_solver(mod, 'gurobi')
if logging_level == 10:
    print_bad_constr(mod, log_fpath)

# print output:
rows = months.copy()
columns = oils.copy()
itkeys = ['buyq', 'useq', 'storeq', 'bool_useq']
for varname in itkeys:
    df = pd.DataFrame(columns=columns, index=rows, data=0.0)
    attrval = getattr(mod, varname)
    for month, oil in attrval.keys():
        if abs(attrval[month, oil].value) > 1e-6:
            df.loc[month, oil] = np.round(attrval[month, oil].value, 1)
    print('\n%s\n###########\n' % varname, df)
