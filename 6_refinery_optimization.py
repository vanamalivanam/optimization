from commons import *
"""
CRA crude 1
CRB crude 2
LN light naphtha
MN medium naphtha
HN heavy naphtha
LO light oil
HO heavy oil
R residuum
LNRG light naphtha used to produce reformed gasoline
MNRG medium naphtha used to produce reformed gasoline
HNRG heavy naphtha used to produce reformed gasoline
RG reformed gasoline
LOCGO light oil used to produce cracked gasoline and cracked oil
HOCGO heavy oil used to produce cracked gasoline and cracked oil
CG cracked gasoline
CO cracked oil
LNPMF light naphtha used to produce premium motor fuel
LNRMF light naphtha used to produce regular motor fuel
MNPMF medium naphtha used to produce premium motor fuel
MNRMF medium naphtha used to produce regular motor fuel
HNPMF heavy naphtha used to produce premium motor fuel
HNRMF heavy naphtha used to produce regular motor fuel
RGPMF reformed gasoline used to produce premium motor fuel
RGRMF reformed gasoline used to produce regular motor fuel
CGPMF cracked gasoline used to produce premium motor fuel
CGRMF cracked gasoline used to produce regular motor fuel
LOJF light oil used to produce jet fuel
HOJF heavy oil used to produce jet fuel
RJF residuum used to produce jet fuel
COJF cracked oil used to produce jet fuel
RLBO residuum used to produce lube-oil
PMF premium motor fuel
RMF regular motor fuel
JF jet fuel
FO fuel oil
LBO lube-oil
"""

mod = pe.ConcreteModel()
all_items = ['cra', 'crb', 'ln', 'mn', 'hn', 'lo', 'ho', 'r', 'lnrg', 'mnrg', 'hnrg', 'rg', 'locgo', 'hocgo', 'cg',
             'co', 'lnpmf', 'lnrmf', 'mnpmf', 'mnrmf', 'hnpmf', 'hnrmf', 'rgpmf', 'rgrmf', 'cgpmf', 'cgrmf', 'lojf',
             'hojf', 'rjf', 'cojf', 'rlbo', 'pmf', 'rmf', 'jf', 'fo', 'lbo']
# this is pyomo variable that needs to be solved.
mod.q = pe.Var(all_items, within=pe.NonNegativeReals, initialize=0)

crude_lim = {'cra': 20000, 'crb': 30000}
crudes = list(crude_lim.keys())

mod.crude_lim_con = pe.ConstraintList()
for cr in crudes:
    mod.crude_lim_con.add(mod.q[cr] <= crude_lim[cr])

# crude oil distillation; naphta reforming; oil(heavy, light) cracking
process_limit = {'crude12': 45000, 'nprg': 10000, 'cracking': 8000}
nprg = ['lnrg', 'mnrg', 'hnrg']
cracking = ['locgo', 'hocgo']
mod.crude_proc_con = pe.Constraint(expr=sum(mod.q[c] for c in crudes) <= process_limit['crude12'])
mod.nap_proc_con = pe.Constraint(expr=sum(mod.q[n] for n in nprg) <= process_limit['nprg'])
mod.cracked_proc_con = pe.Constraint(expr=sum(mod.q[cr] for cr in cracking) <= process_limit['cracking'])
# lube oil constraints lower and upper bounds
mod.lubeoil_lb_con = pe.Constraint(expr=mod.q['lbo'] >= 500)
mod.lubeoil_ub_con = pe.Constraint(expr=mod.q['lbo'] <= 1000)

# Distillation: crude oil to naphtas and oils
# The fractions into which one barrel of each type of crude splits are given
# N.B. There is a small amount of wastage in distillation.
co_yield = {'cra': {'ln': 0.1, 'mn': 0.2, 'hn': 0.2, 'lo': 0.12, 'ho': 0.2, 'r': 0.13},  # sums to 0.95
            'crb': {'ln': 0.15, 'mn': 0.25, 'hn': 0.18, 'lo': 0.08, 'ho': 0.19, 'r': 0.12}  # sums to 0.97
            }
critems = ['ln', 'mn', 'hn', 'lo', 'ho', 'r']
mod.cr_yield_con = pe.ConstraintList()
for it in critems:
    # this is a decomposition constraint, rather than processing limit constraint.
    mod.cr_yield_con.add(mod.q[it] - mod.q['cra'] * co_yield['cra'][it] - mod.q['crb'] * co_yield['crb'][it] == 0)

# reforming process: napthas to reformed_gasoline for three different kinds of napthas.
# gasoline yield in barrels per barrel of naptha type low, medium and high
nrg_d = {'ln': 0.6, 'mn': 0.52, 'hn': 0.45}
mod.reformed_gas_con = pe.Constraint(expr=sum(mod.q['%srg' % i] * nrg_d[i] for i in nrg_d) - mod.q['rg'] == 0)

# rgrmf + rgpmf  = rg
mod.rg_total_con = pe.Constraint(expr=mod.q['rgrmf'] + mod.q['rgpmf'] - mod.q['rg'] == 0)
mod.cracked_oil = pe.Constraint(expr=mod.q['locgo'] * 0.68 + mod.q['hocgo'] * 0.75 - mod.q['co'] == 0)
mod.cracked_gasoline = pe.Constraint(expr=mod.q['locgo'] * 0.28 + mod.q['hocgo'] * 0.2 - mod.q['cg'] == 0)
# Residuum can be used for either producing lube-oil or blending into jet fuel and fuel oil:
# resid_yield = {'lubeoil': 0.5}
mod.lube_yield = pe.Constraint(expr=mod.q['lbo'] - 0.5 * mod.q['rlbo'] == 0)

# sum of all uses of light naptha must equate to ln
mod.sum_nap_con = pe.ConstraintList()
for i in ['ln', 'mn', 'hn']:
    mod.sum_nap_con.add(mod.q['%srg' % i] + mod.q['%spmf' % i] + mod.q['%srmf' % i] + - mod.q[i] == 0)

fuel_ratio = {'lo': 10 / 18.0, 'co': 4 / 18.0, 'ho': 3 / 18.0, 'r': 1 / 18.0}
mod.sum_oil_con = pe.ConstraintList()
# for j in ['lo', 'ho', 'co', 'r']:
mod.sum_oil_con.add(mod.q['lo'] - mod.q['locgo'] - mod.q['lojf'] - fuel_ratio['lo'] * mod.q['fo'] == 0)
mod.sum_oil_con.add(mod.q['ho'] - mod.q['hocgo'] - mod.q['hojf'] - fuel_ratio['ho'] * mod.q['fo'] == 0)
mod.sum_oil_con.add(mod.q['co'] - mod.q['cojf'] - fuel_ratio['co'] * mod.q['fo'] == 0)
mod.sum_oil_con.add(mod.q['r'] - mod.q['rlbo'] - mod.q['rjf'] - fuel_ratio['r'] * mod.q['fo'] == 0)

# Premium petrol production must be at least 40% of regular petrol
# petrol is also called as "motor fuel"
mod.pmf_mass = pe.Constraint(
    expr=mod.q['pmf'] -
    mod.q['lnpmf'] -
    mod.q['mnpmf'] -
    mod.q['hnpmf'] -
    mod.q['rgpmf'] -
    mod.q['cgpmf'] == 0)
mod.rmf_mass = pe.Constraint(
    expr=mod.q['rmf'] -
    mod.q['lnrmf'] -
    mod.q['mnrmf'] -
    mod.q['hnrmf'] -
    mod.q['rgrmf'] -
    mod.q['cgrmf'] == 0)
mod.jf_mass = pe.Constraint(
    expr=mod.q['jf'] -
    mod.q['lojf'] -
    mod.q['hojf'] -
    mod.q['cojf'] -
    mod.q['rjf'] == 0)
mod.reg_prem_ratio = pe.Constraint(expr=mod.q['pmf'] - 0.4 * mod.q['rmf'] >= 0)

# Blending:
# There are two sorts of petrol, regular and premium, obtained by blending the naphtha,
# reformed gasoline and cracked gasoline. The only stipulations concerning them are that
# regular must have an octane number of at least 84 and that premium must have an octane number
# of at least 94. It is assumed that octane numbers blend linearly by volume.

octanes = {'ln': 90, 'mn': 80, 'hn': 70, 'rg': 115, 'cg': 105}
req = {'rmf': 84, 'pmf': 94}
mod.oct_con = pe.ConstraintList()
for i in ['rmf', 'pmf']:
    mod.oct_con.add(sum(mod.q['%s%s' % (r, i)] * octanes[r] for r in octanes) - req[i] * mod.q[i] >= 0)

# 12.6.4.2 Jet fuel
# The stipulation concerning jet fuel is that its vapour pressure must not exceed
# 1 kg cm2. It may again be assumed that vapour pressures blend linearly by volume.
vape = {'lo': 1.0, 'ho': 0.6, 'co': 1.5, 'r': 0.05}
mod.jetfuel_pres_con = pe.Constraint(expr=sum(vape[i] * mod.q['%sjf' % i] for i in vape.keys()) - mod.q['jf'] <= 0)

profit = {'pmf': 7.00, 'rmf': 6.00, 'jf': 4.00, 'fo': 3.50, 'lbo': 1.50}


def rule_obj(mod):
    expr = sum(mod.q[pr] * profit[pr] for pr in profit.keys())
    return


mod.objective = pe.Objective(rule=sum(mod.q[pr] * profit[pr] for pr in profit.keys()), sense=pe.maximize)
# mod.objective = pe.Objective(rule=rule_obj, sense=pe.maximize)
results, log_fpath = run_solver(mod)
# print(results)

# display output
for v in mod.component_objects(pe.Var, active=True):
    print("Variable component object", v)
    for index in v:
        print("   ", index, v[index].value)
"""
profit = {'pmf': 700, 'rmf': 600, 'jf': 400, 'fo': 350, 'lbo': 150}
answer from pyomo:
pmf_q = 769.2307692307693
rmf_q = 1923.0769230769233
jf_q = 2263.02729528536
fo_q = 0.0
lbo_q = 499.99999999999994

700*pmf_q+ 600*rmf_q + 400*jf_q + 350*fo_q + 150*lbo_q
= 2672518.6104218364
"""

"""
optimal answer :
optimal objective: 211365.1348e+05

end_prod[Premium_fuel] = 6817.78
end_prod[Regular_fuel] = 17044.45
end_prod[Jet_fuel] = 15156.0
end_prod[Lube_oil] = 500.0
"""
