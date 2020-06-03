#!/usr/bin/env python
import logging
import sys
# from pyomo.core import Piecewise
from os import name as osname, path, sep

from pyomo import environ as pe

modpath = path.abspath(__file__)
dir_path = path.dirname(modpath)
sys.path.append(dir_path)
initpathlist = path.realpath(__file__).split(sep)

PROJ_PATH = sep.join(initpathlist[:-1])
EXP = initpathlist[-2]

DATA_PATH = sep.join(initpathlist[:-1] + ['data'])
SOLVERS_PATH = sep.join(initpathlist[:-1] + ['solvers'])
print(SOLVERS_PATH)
print(DATA_PATH)
exepath = path.join(SOLVERS_PATH, 'scipampl601')
print(exepath)

oils = ['1', '2', '3', '4', '5']

model = pe.ConcreteModel()
"""
model.buy_qty = pe.Var(oils, initialize=_qtyinit, bounds=_qbounds,
                      within=pe.NonNegativeReals)
# ['u1a', 'u2a', 'u3a', 'u4a', 'u5a']
model.use_qty = pe.Var(oils, initialize=_qtyinit, bounds=_qbounds,
                      within=pe.NonNegativeReals)
# ['s1a','s2a','s3a','s4a','s5a']
model.store_qty = pe.Var(oils, initialize=_qtyinit, bounds=_qbounds,
                      within=pe.NonNegativeReals)
"""
for mon in ['jan', 'feb', 'march', 'april', 'may', 'june']:
    for qty in ['buy_qty', 'use_qty', 'store_qty']:
        cname = qty + '_' + mon
        setattr(model, cname, pe.Var(oils, within=pe.NonNegativeReals, initialize=0))

# quantity of product generated.
model.ya = pe.Var(within=pe.NonNegativeReals, initialize=0)
model.yb = pe.Var(within=pe.NonNegativeReals, initialize=0)
model.yc = pe.Var(within=pe.NonNegativeReals, initialize=0)
model.yd = pe.Var(within=pe.NonNegativeReals, initialize=0)
model.ye = pe.Var(within=pe.NonNegativeReals, initialize=0)
model.yf = pe.Var(within=pe.NonNegativeReals, initialize=0)
# purchase cost of each month for oil1, oil2, oil3, oil4, oil5
futures_jan = [110, 120, 130, 110, 115]
futures_feb = [130, 130, 110, 90, 115]
futures_march = [110, 140, 130, 100, 95]
futures_april = [120, 110, 120, 120, 125]
futures_may = [110, 120, 150, 110, 105]
futures_june = [90, 100, 140, 80, 135]

# oil densities
densities = {'1': 8.8, '2': 6.1, '3': 2, '4': 4.2, '5': 5}

# JAN
#######
# bought used and stored of veg and non veg oils for jan
# b1a, u1a, s1a
# b2a, u2a, s2a
# b3a, u3a, s3a
# b4a, u4a, s4a
# b5a, u5a, s5a


# profit for jan
# ['buy_qty', 'use_qty', 'store_qty']
# pa = −110*b1a − 120*b2a − 130*b3a − 110*b4a − 115*b5a + 150*ya - 5*(s1a+s2a+s3a+s4a+s5a)
model.pa = pe.Expression(expr=150 * model.ya - sum(futures_jan[enm] * model.buy_qty_jan[oid]
                                for enm, oid in enumerate(oils)) - 5 * sum(model.store_qty_jan[oid] for oid in oils))
model.pb = pe.Expression(expr=150 * model.yb - sum(futures_feb[enm] * model.buy_qty_feb[oid]
                                for enm, oid in enumerate(oils)) - 5 * sum(model.store_qty_feb[oid] for oid in oils))
model.pc = pe.Expression(expr=150 * model.yc - sum(futures_march[enm] * model.buy_qty_march[oid]
                                for enm, oid in enumerate(oils)) - 5 * sum(model.store_qty_march[oid] for oid in oils))
model.pd = pe.Expression(expr=150 * model.yd - sum(futures_april[enm] * model.buy_qty_april[oid]
                                for enm, oid in enumerate(oils)) - 5 * sum(model.store_qty_april[oid] for oid in oils))
model.pe = pe.Expression(expr=150 * model.ye - sum(futures_may[enm] * model.buy_qty_may[oid]
                                for enm, oid in enumerate(oils)) - 5 * sum(model.store_qty_may[oid] for oid in oils))
model.pf = pe.Expression(expr=150 * model.yf - sum(futures_june[enm] * model.buy_qty_june[oid]
                                for enm, oid in enumerate(oils)) - 5 * sum(model.store_qty_june[oid] for oid in oils))


def objective_expr(model):
    expr = model.pa + model.pb + model.pc + model.pd + model.pe + model.pf
    return expr


model.objective = pe.Objective(rule=objective_expr, sense=pe.maximize)
# model.objective_expr = pe.Expression(rule=generic_objective)

# hardness upper and lower bound
# Ha = 8.8*u1a + 6.1*u2a + 2*u3a + 4.2*u4a + 5*u5a
# 3*ya <= Ha <= 6*ya
model.Ha = sum(densities[oid] * model.use_qty_jan[oid] for oid in oils)
model.hardnes_jan_low = pe.Constraint(expr=3 * model.ya <= model.Ha)
model.hardnes_jan_high = pe.Constraint(expr=model.Ha <= 6 * model.ya)

model.Hb=sum(densities[oid] * model.use_qty_feb[oid] for oid in oils)
model.hardnes_feb_low =pe.Constraint(expr = 3 * model.yb <= model.Hb)
model.hardnes_feb_high = pe.Constraint(expr = model.Hb <= 6 * model.yb)

model.Hc=sum(densities[oid] * model.use_qty_march[oid] for oid in oils)
model.hardnes_march_low = pe.Constraint(expr=3*model.yc <= model.Hc)
model.hardnes_march_high = pe.Constraint(expr=model.Hc <= 6 * model.yc)

model.Hd=sum(densities[oid] * model.use_qty_april[oid] for oid in oils)
model.hardnes_april_low = pe.Constraint(expr=3*model.yd <= model.Hd)
model.hardnes_april_high = pe.Constraint(expr=model.Hd <= 6 * model.yd)

model.He=sum(densities[oid] * model.use_qty_may[oid] for oid in oils)
model.hardnes_may_low = pe.Constraint(expr=3 * model.ye <= model.He)
model.hardnes_may_high = pe.Constraint(expr=model.He <= 6 * model.ye)

model.Hf=sum(densities[oid] * model.use_qty_june[oid] for oid in oils)
model.hardnes_june_low = pe.Constraint(expr=3 * model.yf <= model.Hf)
model.hardnes_june_high = pe.Constraint(expr=model.Hf <= 6 * model.yf)

# storage limit of 1000 tonnes
# s1a <= 1000
# s2a <= 1000
# s3a <= 1000
# s4a <= 1000
# s5a <= 1000
for oid in oils:
    cname='storage_jan_' + oid
    setattr(model, cname, pe.Constraint(expr=model.store_qty_jan[oid] <= 1000))

    cname='storage_feb_' + oid
    setattr(model, cname, pe.Constraint(expr=model.store_qty_feb[oid] <= 1000))

    cname='storage_march_' + oid
    setattr(model, cname, pe.Constraint(expr=model.store_qty_march[oid] <= 1000))

    cname='storage_april_' + oid
    setattr(model, cname, pe.Constraint(expr=model.store_qty_april[oid] <= 1000))

    cname='storage_may_' + oid
    setattr(model, cname, pe.Constraint(expr=model.store_qty_may[oid] <= 1000))

    cname='storage_june_' + oid
    setattr(model, cname, pe.Constraint(expr=model.store_qty_june[oid] <= 1000))

# volumes must equate for each month.
# u1a + u2a + u3a + u4a + u5a = ya
model.vol_jan_constr=pe.Constraint(expr=sum(model.use_qty_jan[oid] for oid in oils) - model.ya == 0)
model.vol_feb_constr=pe.Constraint(expr=sum(model.use_qty_feb[oid] for oid in oils) - model.yb == 0)
model.vol_march_constr=pe.Constraint(expr=sum(model.use_qty_march[oid] for oid in oils) - model.yc == 0)
model.vol_april_constr=pe.Constraint(expr=sum(model.use_qty_april[oid] for oid in oils) - model.yd == 0)
model.vol_may_constr=pe.Constraint(expr=sum(model.use_qty_may[oid] for oid in oils) - model.ye == 0)
model.vol_june_constr=pe.Constraint(expr=sum(model.use_qty_june[oid] for oid in oils) - model.yf == 0)


# FEB
#######
# bought used and stored of veg and non veg oils for feb
# b1b, u1b, s1b
# b2b, u2b, s2b
# b3b, u3b, s3b
# b4b, u4b, s4b
# b5b, u5b, s5b

# profit for feb
# pb = −130*b1b − 130*b2b − 110*b3b − 90*b4b − 115*b5b + 150*yb - 5*(s1b+s2b+s3b+s4b+s5b)
# hardness upper and lower bound
# Hb = 8.8*u1b + 6.1*u2b + 2*u3b + 4.2*u4b + 5*u5b
# 3*yb <= Hb <= 6*yb

# storage limit of 1000 tonnes
# s1b <= 1000
# s2b <= 1000
# s3b <= 1000
# s4b <= 1000
# s5b <= 1000

# volumes must equate for each month.
# u1b + u2b + u3b + u4b + u5b = yb


# MARCH
#######
# bought used and stored of veg and non veg oils for march
# b1c, u1c, s1c
# b2c, u2c, s2c
# b3c, u3c, s3c
# b4c, u4c, s4c
# b5c, u5c, s5c

# profit for march
# pc = −110*b1c − 140*b2c − 130*b3c − 100*b4c − 95*b5c + 150*yc  - 5*(s1c+s2c+s3c+s4c+s5c)

# hardness upper and lower bound
# Hc = 8.8*u1c + 6.1*u2c + 2*u3c + 4.2*u4c + 5*u5c
# 3*yc <= Hc <= 6*yc

# storage limit of 1000 tonnes
# s1c <=1000
# s2c <=1000
# s3c <=1000
# s4c <=1000
# s5c <=1000

# volumes must equate for each month.
# u1c + u2c + u3c + u4c + u5c = yc


# APRIL
#######
# bought used and stored of veg and non veg oils for april
# b1d, u1d, s1d
# b2d, u2d, s2d
# b3d, u3d, s3d
# b4d, u4d, s4d
# b5d, u5d, s5d


# profit for april
# pd = −120*b1d − 110*b2d − 120*b3d − 120*b4d − 125*b5d + 150*yd - 5*(s1d+s2d+s3d+s4d+s5d)

# hardness upper and lower bound
# Hd = 8.8*u1 + 6.1*u2 + 2*u3 + 4.2*u4 + 5*u5
# 3*yd <= Hd <= 6*yd

# storage limit of 1000 tonnes
# s1d <=1000
# s2d <=1000
# s3d <=1000
# s4d <=1000
# s5d <=1000

# volumes must equate for each month.
# u1d + u2d + u3d + u4d + u5d = yd

# MAY
#######
# bought used and stored of veg and non veg oils for may
# bv1e, uv1e, sv1e
# bv2e, uv2e, sv2e
# bn1e, un1e, sn1e
# bn2e, un2e, sn2e
# bn3e, un3e, sn3e

# profit for may
# pe = −90*b1e − 100*b2e − 140*b3e − 80*b4e − 135*b5e + 150*ye - 5*(s1e+s2e+s3e+s4e+s5e)

# hardness upper and lower bound
# He = 8.8*u1 + 6.1*u2 + 2*u3 + 4.2*u4 + 5*u5
# 3*ye <= He <= 6*ye

# storage limit of 1000 tonnes
# s1e <=1000
# s2e <=1000
# s3e <=1000
# s4e <=1000
# s5e <=1000

# volumes must equate for each month.
# u1e + u2e + u3e + u4e + u5e = ye

# JUNE
#######
# bought used and stored of veg and non veg oils for june
# b1f, u1f, s1f
# b2f, u2f, s2f
# b3f, u3f, s3f
# b4f, u4f, s4f
# b5f, u5f, s5f

# profit for june
# pf = −110*b1f − 120*b2f − 130*b3f − 110*b4f − 115*b5f + 150*yf

# hardness upper and lower bound
# Hf = 8.8*u1 + 6.1*u2 + 2*u3 + 4.2*u4 + 5*u5
# 3*yf <= Hf <= 6*yf

# storage limit of 1000 tonnes
# s1f <=1000
# s2f <=1000
# s3f <=1000
# s4f <=1000
# s5f <=1000

# volumes must equate for each month.
# u1f + u2f + u3f + u4f + u5f = yf


# let ya, yb, yc, yd, ye, yf be the amounts of product produced for jan, feb, march, april, may and june.
# Profit = selling_price - cost_price - storage_price
# let pa, pb, pc, pd, pe, pf be the profits earned for each month.
# total_profit =  pa + pb + pc + pd + pe + pf


"""
# from explanation in the book.
BVEG 11 − UVEG 11 − SVEG 11 = −500,
SVEG 11 + BVEG 12 − UVEG 12 − SVEG 12 = 0,
SVEG 12 + BVEG 13 − UVEG 13 − SVEG 13 = 0,
SVEG 13 + BVEG 14 − UVEG 14 − SVEG 14 = 0,
SVEG 14 + BVEG 15 − UVEG 15 − SVEG 15 = 0,
SVEG 15 + BVEG 16 − UVEG 16 = 500
"""

# for mon in ['jan', 'feb', 'march', 'april', 'may', 'june']:
#     for qty in ['buy_qty', 'use_qty', 'store_qty']:
#         cname = qty + '_' + mon

# for oil 1
# b1a + 500 = u1a + s1a
# s1a + b1b = u1b + s1b
# s1b + b1c = u1c + s1c
# s1c + b1d = u1d + s1d
# s1d + b1e = u1e + s1e
# s1e + b1f = u1f + 500

for oid in oils:
    cname = 'oil_%s_balance_constr_'%oid
    setattr(model, cname+'p', pe.Constraint(expr=model.buy_qty_jan[oid] + 500 == model.use_qty_jan[oid] + model.store_qty_jan[oid] ))
    setattr(model, cname+'q', pe.Constraint(expr=model.store_qty_jan[oid] + model.buy_qty_feb[oid] == model.use_qty_feb[oid] + model.use_qty_feb[oid]))
    setattr(model, cname+'r', pe.Constraint(expr=model.store_qty_feb[oid] + model.buy_qty_march[oid] == model.use_qty_march[oid] + model.use_qty_march[oid]))
    setattr(model, cname+'s', pe.Constraint(expr=model.store_qty_march[oid] + model.buy_qty_april[oid] == model.use_qty_april[oid] + model.use_qty_april[oid]))
    setattr(model, cname+'t', pe.Constraint(expr=model.store_qty_april[oid] + model.buy_qty_may[oid] == model.use_qty_may[oid] + model.use_qty_may[oid]))
    setattr(model, cname+'u', pe.Constraint(expr=model.store_qty_may[oid] + model.buy_qty_june[oid] == model.use_qty_june[oid] + 500))

# for oil 2
# b2a − u2a − s2a = −500
# s2a + b2b − u2b − s2b = 0
# s2b + b2c − u2c − s2c = 0
# s2c + b2d − u2d − s2d = 0
# s2d + b2e − u2e − s2e = 0
# s2e + b2f − u2f = 500

# for oil 3
# b3a − u3a − s3a = −500
# s3a + b3b − u3b − s3b = 0
# s3b + b3c − u3c − s3c = 0
# s3c + b3d − u3d − s3d = 0
# s3d + b3e − u3e − s3e = 0
# s3e + b3f − u3f = 500

# for oil 4
# b4a − u4a − s4a = −500
# s4a + b4b − u4b − s4b = 0
# s4b + b4c − u4c − s4c = 0
# s4c + b4d − u4d − s4d = 0
# s4d + b4e − u4e − s4e = 0
# s4e + b4f − u4f = 500

# for oil 5
# b5a − u5a − s5a = −500
# s5a + b5b − u5b − s5b = 0
# s5b + b5c − u5c − s5c = 0
# s5c + b5d − u5d − s5d = 0
# s5d + b5e − u5e − s5e = 0
# s5e + b5f − u5f = 500

solver = pe.SolverFactory('scip6', executable=exepath, solver_io='nl')
if not path.isfile(exepath):
    logging.error('Error in path to solver file.')
if osname == 'nt':
    logging.error('cannot run solver in windows.')
    # raise SystemExit
    pass
logging.info('starting solver...')
results = solver.solve(model, keepfiles=True, tee=False,
                       report_timing=False, load_solutions=False)
print('solver message:%s'%results.solver.message)
print('term_cond: %s'%results.solver.termination_condition.__str__())
print('solver_status: %s'%results.solver.status.__str__())


def print_vars_debug(m, vartype=pe.Constraint, c1='$', c2='%'):
    # Displays constraints upper bound lower bound and expression.
    # m.display()
    # debugging: constraints defined in the model.
    # logging.debug(peobj.model.display())
    s1 = c1 * 80
    s2 = c2 * 80
    for con in m.component_map(vartype).itervalues():
        # for con in m.component_map(vartype).itervalues():
        print(s1)
        con.pprint()
        print(s2)


if len(results.solution) > 0:
    model.solutions.load_from(results)
    print('objective value: %d' % model.objective())

logging_level = 20
if logging_level == 10:
    from pyomo import environ as pe
    print_vars_debug(model, pe.Constraint, '^', '#')
    print_vars_debug(model, pe.Var, '&', '+')
    print(80 * '&')
    model.display()
    # Qtyvar = getattr(model, 'Qtyvar')
print('printing results')
print('='*20)
print(results)
print('='*20)

log_fpath = solver._log_file
print('log file path: %s'%log_fpath)

logging.info('finished running solver...')
print('results.solver.message: %s'%results.solver.message)

# read the log file created by solver and look for text '<_scon[' to find the failed constr.
# this logic is specific to scip solver's log.
f = open(log_fpath, 'r')
lines = f.read()
pos1 = lines.find('<_scon[')
pos2 = lines.find(']', pos1)
# infeasible constraint:   [linear] <_scon[49]>: <_svar[1]>[C] (+0) -<_svar[6]>[C] (+0) -<_svar[11]>[C] (+0) == -500;
try:
    # result_dict['failed_constr_num'] = int(lines[pos1 + 7: pos2])
    print('@'*20)
    print (lines)
    print('@'*30)
except ValueError as e:
    logging.warning('parser failed to find questionable constraint in logfile: %s' % log_fpath)
    pass
