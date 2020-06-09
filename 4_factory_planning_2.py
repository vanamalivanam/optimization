#!/usr/bin/env python
# problem 4
from pyomo import environ as pe

from commons import run_solver, output_to_display

items = ['p1', 'p2', 'p3', 'p4', 'p5', 'p6', 'p7']
# prods = ['p1', 'p2', 'p3', 'p4', 'p5', 'p6', 'p7']
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

m = pe.ConcreteModel()
# quantity of products that are to be produced for each month
m.qty_made = pe.Var(items, months, initialize=0, within=pe.NonNegativeReals)
m.qty_sold = pe.Var(items, months, initialize=0, within=pe.NonNegativeReals)
m.qty_stored = pe.Var(items, months, initialize=0, within=pe.NonNegativeReals)
# print(list(m.qty_sold.keys()))

eqtype = ['gr', 'vd', 'hd', 'bo', 'pl']
profit = {'p1': 10, 'p2': 6, 'p3': 8, 'p4': 4, 'p5': 11, 'p6': 9, 'p7': 3}

manuf_hours = {'p1': {'gr': 0.5, 'vd': 0.1, 'hd': 0.2, 'bo': 0.05, 'pl': 0},
               'p2': {'gr': 0.7, 'vd': 0.2, 'hd': 0, 'bo': 0.03, 'pl': 0},
               'p3': {'gr': 0, 'vd': 0, 'hd': 0.8, 'bo': 0, 'pl': 0.01},
               'p4': {'gr': 0, 'vd': 0.3, 'hd': 0, 'bo': 0.07, 'pl': 0},
               'p5': {'gr': 0.3, 'vd': 0, 'hd': 0, 'bo': 0.1, 'pl': 0.05},
               'p6': {'gr': 0.2, 'vd': 0.6, 'hd': 0, 'bo': 0, 'pl': 0},
               'p7': {'gr': 0.5, 'vd': 0, 'hd': 0.6, 'bo': 0.08, 'pl': 0.05}}

m.months = pe.Set(initialize=months)
m.prods = pe.Set(initialize=items)
m.equips = pe.Set(initialize=eqtype)


def rule_objective(m):
    # profit contribution per unit per item per month
    # storage cost 0.5 dollar per unit.
    expr1 = sum(m.qty_sold[(pi, mon)] * profit[pi] - m.qty_stored[(pi, mon)] * 0.5 for pi, mon in zip(items, months))
    # expr2 = sum(m.qty_sold[(pi, mon)] * profit[pi]for pi, mon in zip(items, months))
    print(expr1)
    return expr1


def rule_resource_constr(m, mon, eq):
    # manufacturing hours of each equipment per month
    # there will |months * equipments| constraints = 30 constraints
    # 0.5*p1 + 0.7*p2+0*p3 + 0*p4+0.3*p5 + 0.2*p6+0.5*p7<= 3*24*16 for grinding for jan month
    print('rule resource constraint_%s_%s' % (mon, eq))
    expr = sum(manuf_hours[i][eq] * m.qty_made[(i, mon)] for i in items) <= num_equip[mon][eq] * hrs
    print(expr)
    return expr


m.objective = pe.Objective(rule=rule_objective, sense=pe.maximize)
# this is replaced with another version of constraint
# m.resource_constr = pe.Constraint(m.months, m.equips, rule=rule_resource_constr)
m.qrel_con = pe.ConstraintList()
for i in items:
    # total constraints = 7* 7 = 49
    m.qrel_con.add(m.qty_stored[(i, 'jan')] == m.qty_made[(i, 'jan')] - m.qty_sold[(i, 'jan')])
    m.qrel_con.add(m.qty_stored[(i, 'feb')] == m.qty_made[(i, 'feb')] +
                   m.qty_stored[(i, 'jan')] - m.qty_sold[(i, 'feb')])
    m.qrel_con.add(m.qty_stored[(i, 'mar')] == m.qty_made[(i, 'mar')] +
                   m.qty_stored[(i, 'feb')] - m.qty_sold[(i, 'mar')])
    m.qrel_con.add(m.qty_stored[(i, 'apr')] == m.qty_made[(i, 'apr')] +
                   m.qty_stored[(i, 'mar')] - m.qty_sold[(i, 'apr')])
    m.qrel_con.add(m.qty_stored[(i, 'may')] == m.qty_made[(i, 'may')] +
                   m.qty_stored[(i, 'apr')] - m.qty_sold[(i, 'may')])
    m.qrel_con.add(m.qty_stored[(i, 'jun')] == m.qty_made[(i, 'jun')] +
                   m.qty_stored[(i, 'may')] - m.qty_sold[(i, 'jun')])
    # but end of june stock is 50 units per product.
    m.qrel_con.add(50 == m.qty_stored[(i, 'jun')])

#                       jan, feb, mar,apr, may, jun
market_limits = {'p1': [500, 600, 300, 200, 0, 500],
                 'p2': [1000, 500, 600, 300, 100, 500],
                 'p3': [300, 200, 0, 400, 500, 100],
                 'p4': [300, 0, 0, 500, 100, 300],
                 'p5': [800, 400, 500, 200, 1000, 1100],
                 'p6': [200, 300, 400, 0, 300, 500],
                 'p7': [100, 150, 100, 100, 0, 60]}

# m.market_lim = pe.ConstraintList()
# m.storage_lim = pe.ConstraintList()
cname1 = 'market_lim_'
cname2 = 'storage_lim_'
for it in items:
    # number of constraints = 2 *7 * 6 = 84
    for enm, mon in enumerate(months):
        s1 = it + '_' + mon
        setattr(m, cname1 + s1, pe.Constraint(expr=m.qty_sold[it, mon] <= market_limits[it][enm]))
        # max storage capacity per month per product type = 100
        setattr(m, cname2 + s1, pe.Constraint(expr=m.qty_stored[it, mon] <= 100))


# copied above code from 3_factory_planning_1.py


# total equipments before repairs : 4, 2, 3, 1, 1
equip_qty = {'gr': 4, 'vd': 2, 'hd': 3, 'bo': 1, 'pl': 1}
"""
Instead of stipulating when each machine is down for maintenance in the factory
planning problem, it is desired to find the best month for each machine to be
down.
Each machine must be down for maintenance in one month of the six apart
from the grinding machines, only two of which need be down in any six months.
"""

def _qbounds(m, mon, eq):
    if eq == 'gr':
        return (0, 2)
    else:
        return (0,1)
m.bool_eqp = pe.Var(m.months, m.equips, within=pe.NonNegativeIntegers, initialize=0, bounds=_qbounds)

def rule_resource_constr2(m, mon, eq):
    # manufacturing hours of each equipment per month;
    expr = sum(manuf_hours[i][eq] * m.qty_made[(i, mon)] for i in items) <= (num_equip[mon][eq] - m.bool_eqp[mon, eq])*hrs
    return expr

def rule_one_eqp_down_per_month_constr(m, mon):
    expr = sum(m.bool_eqp[mon, eq] for eq in m.equips) <= 1
    return expr

def rule_once_downtime_per_eqp_constr(m, eq):
    if eq == 'gr':
        expr = sum(m.bool_eqp[mon, eq] for mon in m.months) == 2
    else:
        expr = sum(m.bool_eqp[mon,eq] for mon in m.months) == 1
    return expr

m.one_res_down_permon_constr = pe.Constraint(m.months, rule=rule_one_eqp_down_per_month_constr)
m.one_res_down_constr = pe.Constraint(m.equips, rule=rule_once_downtime_per_eqp_constr)
m.resource_constr = pe.Constraint(m.months, m.equips, rule=rule_resource_constr2)


results, log_fpath = run_solver(m)
# output_to_display(m, ['qty_made', 'qty_sold', 'qty_stored'])
