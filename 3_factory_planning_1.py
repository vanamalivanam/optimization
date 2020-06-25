# problem 3
from itertools import product

import numpy as np
import pandas as pd

from commons import *

items = ['p1', 'p2', 'p3', 'p4', 'p5', 'p6', 'p7']
months = ['jan', 'feb', 'mar', 'apr', 'may', 'jun']
# working days: 24/month; working hours : 8; number of shifts : 2
hrs = 24 * 8 * 2
# total equipments before repairs : 4, 2, 3, 1, 1
num_equip = {'jan': {'gr': 3, 'vd': 2, 'hd': 3, 'bo': 1, 'pl': 1},
             'feb': {'gr': 4, 'vd': 2, 'hd': 1, 'bo': 1, 'pl': 1},
             'mar': {'gr': 4, 'vd': 2, 'hd': 3, 'bo': 0, 'pl': 1},
             'apr': {'gr': 4, 'vd': 1, 'hd': 3, 'bo': 1, 'pl': 1},
             'may': {'gr': 3, 'vd': 1, 'hd': 3, 'bo': 1, 'pl': 1},
             'jun': {'gr': 4, 'vd': 2, 'hd': 2, 'bo': 1, 'pl': 0}}
eqtype = ['gr', 'vd', 'hd', 'bo', 'pl']
profit = {'p1': 10, 'p2': 6, 'p3': 8, 'p4': 4, 'p5': 11, 'p6': 9, 'p7': 3}
manuf_hours = {'p1': {'gr': 0.5, 'vd': 0.1, 'hd': 0.2, 'bo': 0.05, 'pl': 0},
               'p2': {'gr': 0.7, 'vd': 0.2, 'hd': 0, 'bo': 0.03, 'pl': 0},
               'p3': {'gr': 0, 'vd': 0, 'hd': 0.8, 'bo': 0, 'pl': 0.01},
               'p4': {'gr': 0, 'vd': 0.3, 'hd': 0, 'bo': 0.07, 'pl': 0},
               'p5': {'gr': 0.3, 'vd': 0, 'hd': 0, 'bo': 0.1, 'pl': 0.05},
               'p6': {'gr': 0.2, 'vd': 0.6, 'hd': 0, 'bo': 0, 'pl': 0},
               'p7': {'gr': 0.5, 'vd': 0, 'hd': 0.6, 'bo': 0.08, 'pl': 0.05}}
#                       jan, feb, mar,apr, may, jun
market_limits = {'p1': [500, 600, 300, 200, 0, 500],
                 'p2': [1000, 500, 600, 300, 100, 500],
                 'p3': [300, 200, 0, 400, 500, 100],
                 'p4': [300, 0, 0, 500, 100, 300],
                 'p5': [800, 400, 500, 200, 1000, 1100],
                 'p6': [200, 300, 400, 0, 300, 500],
                 'p7': [100, 150, 100, 100, 0, 60]}

m = pe.ConcreteModel()
m.months = pe.Set(initialize=months)
m.prods = pe.Set(initialize=items)
m.equips = pe.Set(initialize=eqtype)

# quantity of products that are to be produced for each month
m.made = pe.Var(items, months, initialize=0, within=pe.NonNegativeReals)
m.sold = pe.Var(items, months, initialize=0, within=pe.NonNegativeReals)
m.stored = pe.Var(items, months, initialize=0, within=pe.NonNegativeReals)


def rule_objective(m):
    # profit contribution per unit per item per month; storage cost 0.5 dollar per unit.
    expr1 = sum(m.sold[(pi, mon)] * profit[pi] - m.stored[(pi, mon)] * 0.5 for pi, mon in product(items, months))
    return expr1


def rule_resource_constr(m, mon, eq):
    # manufacturing hours of each equipment per month
    # there will |months * equipments| constraints = 30 constraints
    # 0.5*p1 + 0.7*p2+0*p3 + 0*p4+0.3*p5 + 0.2*p6+0.5*p7<= 3*24*16 for grinding for jan month
    expr = sum(manuf_hours[i][eq] * m.made[(i, mon)] for i in items) <= num_equip[mon][eq] * hrs
    return expr


m.objective = pe.Objective(rule=rule_objective, sense=pe.maximize)
m.resource_constr = pe.Constraint(m.months, m.equips, rule=rule_resource_constr)
# relative quantites constraint
m.qrel = pe.ConstraintList()
for i in items:
    # total constraints = 7* 7 = 49
    m.qrel.add(m.stored[(i, 'jan')] == m.made[(i, 'jan')] - m.sold[(i, 'jan')])
    m.qrel.add(m.stored[(i, 'feb')] == m.made[(i, 'feb')] +
                   m.stored[(i, 'jan')] - m.sold[(i, 'feb')])
    m.qrel.add(m.stored[(i, 'mar')] == m.made[(i, 'mar')] +
                   m.stored[(i, 'feb')] - m.sold[(i, 'mar')])
    m.qrel.add(m.stored[(i, 'apr')] == m.made[(i, 'apr')] +
                   m.stored[(i, 'mar')] - m.sold[(i, 'apr')])
    m.qrel.add(m.stored[(i, 'may')] == m.made[(i, 'may')] +
                   m.stored[(i, 'apr')] - m.sold[(i, 'may')])
    m.qrel.add(m.stored[(i, 'jun')] == m.made[(i, 'jun')] +
                   m.stored[(i, 'may')] - m.sold[(i, 'jun')])
    # but end of june stock is 50 units per product.
    m.qrel.add(50 == m.stored[(i, 'jun')])

m.market_lim = pe.ConstraintList()
m.storage_lim = pe.ConstraintList()
for it in items:
    # number of constraints = 2 *7 * 6 = 84
    for enm, mon in enumerate(months):
        m.market_lim.add(m.sold[it, mon] - market_limits[it][enm] <= 0)
        m.storage_lim.add(m.stored[it, mon] <= 100)

results, log_fpath = run_solver(m)
# output_to_display(m, ['made', 'sold', 'stored'])
# display output on console
itkeys = {'made':'production plan', 'sold':'sales plan', 'stored':'inventory plan'}
rows = months.copy()
columns = items.copy()
for varname, printval in itkeys.items():
    df = pd.DataFrame(columns=columns, index=rows, data=0.0)
    # store_plan = pd.DataFrame(columns=columns, index=rows, data=0.0)
    attrval = getattr(m, varname)
    for p, mon in attrval.keys():
        if abs(attrval[p, mon].value) > 1e-6:
            df.loc[mon, p] = np.round(attrval[p, mon].value, 1)
    print('\n%s\n###########\n' % varname, df)
