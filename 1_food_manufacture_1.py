#!/usr/bin/env python
logging_level = 20

import logging
import sys
from inspect import stack
from os import name as osname, path, sep

# from pyomo.core import Piecewise
from pyomo import environ as pe
from pyomo.version.info import version_info as pyomoversion

def check_expr(exprarg):
    # supports Pyomo 5.6.5
    # pyomo >= 5.6: is_expression_type(); pyomo <=5.5: is_expression()
    if pyomoversion[1] >= 6:
        if exprarg.is_expression_type():
            return True
    elif pyomoversion[1] == 5:
        if exprarg.is_expression():
            return True
    logging.warning('No expression returned by expr_method: %s called by the parent %s' %
                    (stack()[0][3], stack()[1][3]))
    return False

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


modpath = path.abspath(__file__)
dir_path = path.dirname(modpath)
sys.path.append(dir_path)
initpathlist = path.realpath(__file__).split(sep)

PROJ_PATH = sep.join(initpathlist[:-1])
EXP = initpathlist[-2]

# DATA_PATH = sep.join(initpathlist[:-1] + ['data'])
SOLVERS_PATH = sep.join(initpathlist[:-1] + ['solvers'])
print(SOLVERS_PATH)
exepath = path.join(SOLVERS_PATH, 'scipampl601')
print(exepath)

model = pe.ConcreteModel()
oils = ['1', '2', '3', '4', '5']
vegoils = ['1','2']
nvegoils = ['3','4','5']

for mon in ['jan', 'feb', 'march', 'april', 'may', 'june']:
    for qty in ['buyq', 'useq', 'storeq']:
        cname = qty + '_' + mon
        setattr(model, cname, pe.Var(oils, within=pe.NonNegativeReals, initialize=0))

# In any month, it is not possible to refine more than 200 tons of vegetable oils and
# more than 250 tons of non-vegetable oils.
cname1 = 'vegoil_refinelimit_constr_'
setattr(model, cname1+'a', pe.Constraint(expr=sum(model.useq_jan[oid] for oid in vegoils) <=200))
setattr(model, cname1+'b', pe.Constraint(expr=sum(model.useq_feb[oid] for oid in vegoils) <=200))
setattr(model, cname1+'c', pe.Constraint(expr=sum(model.useq_march[oid] for oid in vegoils) <=200))
setattr(model, cname1+'d', pe.Constraint(expr=sum(model.useq_april[oid] for oid in vegoils) <=200))
setattr(model, cname1+'e', pe.Constraint(expr=sum(model.useq_may[oid] for oid in vegoils) <=200))
setattr(model, cname1+'f', pe.Constraint(expr=sum(model.useq_june[oid] for oid in vegoils) <=200))

cname2 = 'nonvegoil_refinelimit_constr_'
setattr(model, cname2+'a', pe.Constraint(expr=sum(model.useq_jan[oid] for oid in nvegoils) <=250))
setattr(model, cname2+'b', pe.Constraint(expr=sum(model.useq_feb[oid] for oid in nvegoils) <=250))
setattr(model, cname2+'c', pe.Constraint(expr=sum(model.useq_march[oid] for oid in nvegoils) <=250))
setattr(model, cname2+'d', pe.Constraint(expr=sum(model.useq_april[oid] for oid in nvegoils) <=250))
setattr(model, cname2+'e', pe.Constraint(expr=sum(model.useq_may[oid] for oid in nvegoils) <=250))
setattr(model, cname2+'f', pe.Constraint(expr=sum(model.useq_june[oid] for oid in nvegoils) <=250))

# quantity of product generated one variable per month
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
futures_may = [100, 120, 150, 110, 105]
futures_june = [90, 100, 140, 80, 135]

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


# let ya, yb, yc, yd, ye, yf be the amounts of product produced for jan, feb, march, april, may and june.
# Profit = selling_price - cost_price - storage_price
model.pa = pe.Expression(expr=150 * model.ya - sum(futures_jan[enm] * model.buyq_jan[oid]
                                for enm, oid in enumerate(oils)) - 5 * sum(model.storeq_jan[oid] for oid in oils))
model.pb = pe.Expression(expr=150 * model.yb - sum(futures_feb[enm] * model.buyq_feb[oid]
                                for enm, oid in enumerate(oils)) - 5 * sum(model.storeq_feb[oid] for oid in oils))
model.pc = pe.Expression(expr=150 * model.yc - sum(futures_march[enm] * model.buyq_march[oid]
                                for enm, oid in enumerate(oils)) - 5 * sum(model.storeq_march[oid] for oid in oils))
model.pd = pe.Expression(expr=150 * model.yd - sum(futures_april[enm] * model.buyq_april[oid]
                                for enm, oid in enumerate(oils)) - 5 * sum(model.storeq_april[oid] for oid in oils))
model.pe = pe.Expression(expr=150 * model.ye - sum(futures_may[enm] * model.buyq_may[oid]
                                for enm, oid in enumerate(oils)) - 5 * sum(model.storeq_may[oid] for oid in oils))
model.pf = pe.Expression(expr=150 * model.yf - sum(futures_june[enm] * model.buyq_june[oid]
                                for enm, oid in enumerate(oils)) - 5 * sum(model.storeq_june[oid] for oid in oils))

def objective_expr(model):
    # let pa, pb, pc, pd, pe, pf be the profits earned for each month.
    # total_profit =  pa + pb + pc + pd + pe + pf
    expr = model.pa + model.pb + model.pc + model.pd + model.pe + model.pf
    return expr

model.objective = pe.Objective(rule=objective_expr, sense=pe.maximize)


# There is a technological restriction of hardness on the final product. In the units in which hardness is measured,
# this must lie between 3 and 6; hardness has upper and lower bound

# Ha = 8.8*u1a + 6.1*u2a + 2*u3a + 4.2*u4a + 5*u5a
# 3*ya <= Ha <= 6*ya
# similarly for other months Hb, Hc, Hd, He, Hf
# oil densities calculated for each month
densities = {'1': 8.8, '2': 6.1, '3': 2, '4': 4.2, '5': 5}

model.Ha = pe.Expression(expr=sum(densities[oid] * model.useq_jan[oid] for oid in oils))
model.hardnes_jan_low = pe.Constraint(expr=3 * model.ya <= model.Ha)
model.hardnes_jan_high = pe.Constraint(expr=model.Ha <= 6 * model.ya)

model.Hb = pe.Expression(expr=sum(densities[oid] * model.useq_feb[oid] for oid in oils))
model.hardness_feb_low =pe.Constraint(expr = 3 * model.yb <= model.Hb)
model.hardness_feb_high = pe.Constraint(expr = model.Hb <= 6 * model.yb)

model.Hc = pe.Expression(expr=sum(densities[oid] * model.useq_march[oid] for oid in oils))
model.hardness_march_low = pe.Constraint(expr=3*model.yc <= model.Hc)
model.hardness_march_high = pe.Constraint(expr=model.Hc <= 6 * model.yc)

model.Hd = pe.Expression(expr=sum(densities[oid] * model.useq_april[oid] for oid in oils))
model.hardnes_april_low = pe.Constraint(expr=3*model.yd <= model.Hd)
model.hardnes_april_high = pe.Constraint(expr=model.Hd <= 6 * model.yd)

model.He = pe.Expression(expr=sum(densities[oid] * model.useq_may[oid] for oid in oils))
model.hardnes_may_low = pe.Constraint(expr=3 * model.ye <= model.He)
model.hardnes_may_high = pe.Constraint(expr=model.He <= 6 * model.ye)

model.Hf = pe.Expression(expr=sum(densities[oid] * model.useq_june[oid] for oid in oils))
model.hardnes_june_low = pe.Constraint(expr=3 * model.yf <= model.Hf)
model.hardnes_june_high = pe.Constraint(expr=model.Hf <= 6 * model.yf)

# storage limit of 1000 tonnes
# It is possible to store up to 1000 tons of each raw oil for use later. The cost
# of storage for vegetable and non-vegetable oil is £5 per ton per month.
for oid in oils:
    cname='storage_jan_' + oid
    setattr(model, cname, pe.Constraint(expr=model.storeq_jan[oid] <= 1000))
    cname='storage_feb_' + oid
    setattr(model, cname, pe.Constraint(expr=model.storeq_feb[oid] <= 1000))
    cname='storage_march_' + oid
    setattr(model, cname, pe.Constraint(expr=model.storeq_march[oid] <= 1000))
    cname='storage_april_' + oid
    setattr(model, cname, pe.Constraint(expr=model.storeq_april[oid] <= 1000))
    cname='storage_may_' + oid
    setattr(model, cname, pe.Constraint(expr=model.storeq_may[oid] <= 1000))
    cname='storage_june_' + oid
    setattr(model, cname, pe.Constraint(expr=model.storeq_june[oid] <= 1000))

# volumes must equate for each month.
# u1a + u2a + u3a + u4a + u5a = ya
model.vol_jan_constr=pe.Constraint(expr=sum(model.useq_jan[oid] for oid in oils) == model.ya)
model.vol_feb_constr=pe.Constraint(expr=sum(model.useq_feb[oid] for oid in oils) == model.yb)
model.vol_march_constr=pe.Constraint(expr=sum(model.useq_march[oid] for oid in oils) == model.yc)
model.vol_april_constr=pe.Constraint(expr=sum(model.useq_april[oid] for oid in oils) == model.yd)
model.vol_may_constr=pe.Constraint(expr=sum(model.useq_may[oid] for oid in oils) == model.ye)
model.vol_june_constr=pe.Constraint(expr=sum(model.useq_june[oid] for oid in oils )== model.yf)

"""
# from explanation in the book for the month of jan
BVEG 11 − UVEG 11 − SVEG 11 = −500,
SVEG 11 + BVEG 12 − UVEG 12 − SVEG 12 = 0,
SVEG 12 + BVEG 13 − UVEG 13 − SVEG 13 = 0,
SVEG 13 + BVEG 14 − UVEG 14 − SVEG 14 = 0,
SVEG 14 + BVEG 15 − UVEG 15 − SVEG 15 = 0,
SVEG 15 + BVEG 16 − UVEG 16 = 500
"""
# Each oil may be purchased for immediate delivery (January) or bought on the
# futures market for delivery in a subsequent month.
# how the buy, store, and use quantites oils  to be related.
# for oil 1, b1a = 'buy oil 1 for jan'

# b1a + 500 = u1a + s1a
# s1a + b1b = u1b + s1b
# s1b + b1c = u1c + s1c
# s1c + b1d = u1d + s1d
# s1d + b1e = u1e + s1e
# s1e + b1f = u1f + 500
# similarly for oil 2, oil3, oil4, oil5
for oid in oils:
    cname = 'oil_%s_balance_constr_'%oid
    setattr(model, cname+'jan', pe.Constraint(expr=model.buyq_jan[oid] + 500 == model.useq_jan[oid] + model.storeq_jan[oid] ))
    setattr(model, cname+'feb', pe.Constraint(expr=model.storeq_jan[oid] + model.buyq_feb[oid] == model.useq_feb[oid] + model.storeq_feb[oid]))
    setattr(model, cname+'march', pe.Constraint(expr=model.storeq_feb[oid] + model.buyq_march[oid] == model.useq_march[oid] + model.storeq_march[oid]))
    setattr(model, cname+'april', pe.Constraint(expr=model.storeq_march[oid] + model.buyq_april[oid] == model.useq_april[oid] + model.storeq_april[oid]))
    setattr(model, cname+'may', pe.Constraint(expr=model.storeq_april[oid] + model.buyq_may[oid] == model.useq_may[oid] + model.storeq_may[oid]))
    setattr(model, cname+'june', pe.Constraint(expr=model.storeq_may[oid] + model.buyq_june[oid] == model.useq_june[oid] + 500))

solver = pe.SolverFactory('scip6', executable=exepath, solver_io='nl')
if not path.isfile(exepath):
    logging.error('Error in path to solver file.')
if osname == 'nt':
    logging.error('cannot run solver in windows.')
    pass
logging.info('starting solver...')
results = solver.solve(model, keepfiles=True, tee=False,
                       report_timing=False, load_solutions=False)
print('solver message:%s'%results.solver.message)
print('term_cond: %s'%results.solver.termination_condition.__str__())
print('solver_status: %s'%results.solver.status.__str__())

if len(results.solution) > 0:
    model.solutions.load_from(results)
print('objective value: %d' % model.objective())


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


# correct objective value: 107843
# current objective value: 120342