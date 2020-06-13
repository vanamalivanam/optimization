from commons import *
"""
12.6 Refinery optimisation
An oil refinery purchases two crude oils (crude 1 and crude 2). These crude oils
are put through four processes: distillation, reforming, cracking and blending, to
produce petrols and fuels that are sold.
"""
mod = pe.ConcreteModel()
profit = {'premium_petrol': 700, 'regular_petrol': 600,
          'jet_fuel': 400, 'fuel_oil': 350, 'lubeoil': 150}
mod.prods = pe.Set(initialize=profit.keys())
mod.prod_qty = pe.Var(mod.prods, initialize=0, within=pe.NonNegativeReals)
raws_lim = {'crude1': 20000, 'crude2': 30000}
mod.raws = pe.Set(initialize=raws_lim.keys())
def _rbounds(mod, r):
    return (0, raws_lim[r])
mod.crude_qty = pe.Var(mod.raws, initialize=0, bounds=_rbounds, within=pe.NonNegativeReals)
process_limit = {'crude12': 45000, 'nap': 10000, 'cracked': 8000}
mod.crude_proc_constr = pe.Constraint(expr=sum(mod.crude_qty[r] for r in mod.raws) <=process_limit['crude12'])

# Distillation: crude oil to naphtas and oils
# The fractions into which one barrel of each type of crude splits are given
# N.B. There is a small amount of wastage in distillation.
crudeoil_yield = {'crude1': {'lnap': 0.1, 'mnap': 0.2, 'hnap': 0.2, 'loil': 0.12, 'hoil': 0.2, 'res': 0.13},  # sums to 0.95
                  'crude2': {'lnap': 0.15, 'mnap': 0.25, 'hnap': 0.18, 'loil': 0.08, 'hoil': 0.19, 'res': 0.12}  # sums to 0.97
                  }
mod.napth_ids = pe.Set(initialize=['lnap', 'mnap', 'hnap'])
mod.interprods = pe.Set(initialize=['lnap', 'mnap', 'hnap', 'loil', 'hoil', 'res'])
mod.inter_qty = pe.Var(mod.interprods, initialize=0, within=pe.NonNegativeReals)
def _naptha_proc_constr(mod):
    expr = sum(mod.crude_qty[r] * crudeoil_yield[r][nid] for nid, r in mod.napth_ids * mod.raws) <= process_limit['nap']
    return expr
mod.naptha_proc_constr = pe.Constraint(rule=_naptha_proc_constr)
mod.objective = pe.Objective(rule=sum(mod[t]*profit[t] for t in mod.prods), sense=pe.maximize)
# list of constraints
# fracs = ['lnap', 'mnap', 'hnap', 'loil', 'hoil', 'res']
mod.procs = pe.Set(initialize=['distillation', 'reforming', 'cracking', 'blending'])
octanes = {'lnap': 90, 'mnap': 80, 'hnap': 70, 'reformed_gas': 115, 'cracked_gas': 105,
           'regular_petrol': 84, 'premium_petrol': 94}

# reforming process: napthas to reformed_gasoline for three different kinds of napthas.
# gasoline yield in barrels per barrel of naptha type low, medium and high
naptha2_reformed_gasoline = {'lnap': 0.6, 'mnap': 0.52, 'hnap': 0.45}
# cracking process: oils ( light, heavy) to cracked oil/cracked gasoline
crackingoil_yield = {'loil': {'cracked_oil': 0.68, 'cracked_gas': 0.28},
                     'hoil': {'cracked_oil': 0.75, 'cracked_gas': 0.2}}
# Residuum can be used for either producing lube-oil or blending into jet fuel and fuel oil:
mod.lube_qty_constr = pe.Constraint(expr=mod.prods['lubeoil']-mod.inter_qty['res']*0.5==0)
resid_yield = {'lubeoil': 0.5}
# Blending: Cracked oil is used for blending fuel oil and jet fuel; cracked gasoline is used for blending petrol.
# octane numbers blend linearly

# 12.6.4.2 Jet fuel
# The stipulation concerning jet fuel is that its vapour pressure must not exceed
# 1 kg cm2. It may again be assumed that vapour pressures blend linearly by volume.
vapour_pressure = {'loil': 1.0, 'hoil': 0.6, 'cracked_oil': 1.5, 'resid': 0.05}
# fuel_oil
# To produce fuel oil, light oil, cracked oil, heavy oil and residuum must be blended in the ratio 10:4:3:1.
# fuel_oil = 10*loil + 4*cracked_oil + 3*hoil + 1*res
mod.fueloil_q = pe.Var('fueloil', within=pe.NonNegativeReals)
fueloil_r = {'loil':10, 'cracked_oil':4, 'hoil':3, 'res':1}
fueloil_s = sum(fueloil_r.values())
mod.fueloil_con =  pe.Constraint(expr=sum(mod.inter_qty[r]*fueloil_r[r] for r in fueloil_r.keys())-fueloil_s*mod.fueloil_q==0)
mod.lubeoil_prod_lb_con = pe.Constraint(expr=mod.prod_qty['lubeoil']>=500)
mod.lubeoil_prod_ub_con = pe.Constraint(expr=mod.prod_qty['lubeoil']<=1000)

# crude oil distillation; naphta reforming; oil(heavy, light) cracking
process_limit = {'crude12': 45000, 'nap': 10000, 'cracked': 8000}
lubeoil_prod = {'lbound': 500, 'ubound': 1000}  # in barrels
# Premium petrol production must be at least 40% of regular petrol
# petrol is also called as "motor fuel"

# maximize profit

"""
12.6.4 Blending
12.6.4.1 Petrols (motor fuel)
There are two sorts of petrol, regular and premium, obtained by blending the naphtha,
reformed gasoline and cracked gasoline. The only stipulations concerning them are that
regular must have an octane number of at least 84 and that premium must have an octane number
of at least 94. It is assumed that octane numbers blend linearly by volume.
"""
"""
12.6.4.3 Fuel oil
To produce fuel oil, light oil, cracked oil, heavy oil and residuum must be blended
in the ratio 10:4:3:1.
There are availability and capacity limitations on the quantities and processes
used as follows:
1. The daily availability of crude 1 is 20 000 barrels.
2. The daily availability of crude 2 is 30 000 barrels.
3. At most 45 000 barrels of crude can be distilled per day.
4. At most 10 000 barrels of naphtha can be reformed per day.
5. At most 8000 barrels of oil can be cracked per day.
6. The daily production of lube oil must be between 500 and 1000 barrels.
7. Premium motor fuel production must be at least 40% of regular motor fuel
production.
The profit contributions from the sale of the final products are (in pence per
barrel) as follows:
How should the operations of the refinery be planned in order to maximise
total profit?
"""