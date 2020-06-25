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
mod.qty = pe.Var(all_items, within=pe.NonNegativeReals, initialize=0)

crude_lim = {'cra': 20000, 'crb': 30000}
crudes = list(crude_lim.keys())

mod.crude_lim_con = pe.ConstraintList()
for cr in crudes:
    mod.crude_lim_con.add(mod.qty[cr] <= crude_lim[cr])

# crude oil distillation; naphta reforming; oil(heavy, light) cracking
process_limit = {'crude12': 45000, 'nprg': 10000, 'cracking': 8000}
nprg = ['lnrg', 'mnrg', 'hnrg']
cracking = ['locgo', 'hocgo']
mod.crude_proc_con = pe.Constraint(expr=sum(mod.qty[c] for c in crudes) <= process_limit['crude12'])
mod.nap_proc_con = pe.Constraint(expr=sum(mod.qty[n] for n in nprg) <= process_limit['nprg'])
mod.cracked_proc_con = pe.Constraint(expr=sum(mod.qty[cr] for cr in cracking) <= process_limit['cracking'])
# lube oil constraints lower and upper bounds
mod.lubeoil_lb_con = pe.Constraint(expr=mod.qty['lbo'] >= 500)
mod.lubeoil_ub_con = pe.Constraint(expr=mod.qty['lbo'] <= 1000)

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
    mod.cr_yield_con.add(mod.qty[it] - mod.qty['cra']*co_yield['cra'][it] - mod.qty['crb']*co_yield['crb'][it] == 0)

# reforming process: napthas to reformed_gasoline for three different kinds of napthas.
# gasoline yield in barrels per barrel of naptha type low, medium and high
nrg_d = {'ln': 0.6, 'mn': 0.52, 'hn': 0.45}
mod.reformed_gas_con = pe.Constraint(expr=sum(mod.qty['%srg'%i]*nrg_d[i] for i in nrg_d) - mod.qty['rg']==0)

# rgrmf + rgpmf  = rg
mod.rg_total_con = pe.Constraint(expr=mod.qty['rgrmf']+mod.qty['rgpmf']- mod.qty['rg']==0)
mod.cracked_oil = pe.Constraint(expr=mod.qty['locgo'] * 0.68 + mod.qty['hocgo'] * 0.75 - mod.qty['co'] == 0)
mod.cracked_gasoline = pe.Constraint(expr=mod.qty['locgo'] * 0.28 + mod.qty['hocgo'] * 0.2 - mod.qty['cg'] == 0)
# Residuum can be used for either producing lube-oil or blending into jet fuel and fuel oil:
# resid_yield = {'lubeoil': 0.5}
mod.lube_yield = pe.Constraint(expr=mod.qty['lbo'] - 0.5 * mod.qty['rlbo'] == 0)

# sum of all uses of light naptha must equate to ln
mod.sum_nap_con = pe.ConstraintList()
for i in ['ln', 'mn', 'hn']:
    mod.sum_nap_con.add(mod.qty['%srg' % i] + mod.qty['%spmf' % i] + mod.qty['%srmf' % i] + - mod.qty[i] == 0)

fuel_ratio = {'lo': 10 / 18.0, 'co': 4 / 18.0, 'ho': 3 / 18.0, 'r': 1 / 18.0}
mod.sum_oil_con = pe.ConstraintList()
# for j in ['lo', 'ho', 'co', 'r']:
mod.sum_oil_con.add(mod.qty['lo'] - mod.qty['locgo'] - mod.qty['lojf'] - fuel_ratio['lo'] * mod.qty['fo'] == 0)
mod.sum_oil_con.add(mod.qty['ho'] - mod.qty['hocgo'] - mod.qty['hojf'] - fuel_ratio['ho'] * mod.qty['fo'] == 0)
mod.sum_oil_con.add(mod.qty['co']  - mod.qty['cojf'] - fuel_ratio['co'] * mod.qty['fo'] == 0)
mod.sum_oil_con.add(mod.qty['r'] - mod.qty['rlbo'] - mod.qty['rjf'] - fuel_ratio['r'] * mod.qty['fo'] == 0)

# Premium petrol production must be at least 40% of regular petrol
# petrol is also called as "motor fuel"
mod.pmf_mass = pe.Constraint(expr=mod.qty['pmf']-mod.qty['lnpmf']-mod.qty['mnpmf']-mod.qty['hnpmf']-mod.qty['rgpmf']-mod.qty['cgpmf']==0)
mod.rmf_mass = pe.Constraint(expr=mod.qty['rmf']-mod.qty['lnrmf']-mod.qty['mnrmf']-mod.qty['hnrmf']-mod.qty['rgrmf']-mod.qty['cgrmf']==0)
mod.jf_mass = pe.Constraint(expr=mod.qty['jf']-mod.qty['lojf']-mod.qty['hojf']-mod.qty['cojf']-mod.qty['rjf']==0)
mod.reg_prem_ratio = pe.Constraint(expr=mod.qty['pmf'] - 0.4 * mod.qty['rmf'] >= 0)

# Blending:
# There are two sorts of petrol, regular and premium, obtained by blending the naphtha,
# reformed gasoline and cracked gasoline. The only stipulations concerning them are that
# regular must have an octane number of at least 84 and that premium must have an octane number
# of at least 94. It is assumed that octane numbers blend linearly by volume.

octanes = {'ln': 90, 'mn': 80, 'hn': 70, 'rg': 115, 'cg': 105}
req = {'rmf': 84, 'pmf': 94}
mod.oct_con = pe.ConstraintList()
for i in ['rmf', 'pmf']:
    mod.oct_con.add(sum(mod.qty['%s%s' % (r, i)] * octanes[r] for r in octanes) - req[i] * mod.qty[i] >= 0)

# 12.6.4.2 Jet fuel
# The stipulation concerning jet fuel is that its vapour pressure must not exceed
# 1 kg cm2. It may again be assumed that vapour pressures blend linearly by volume.
vape = {'lo': 1.0, 'ho': 0.6, 'co': 1.5, 'r': 0.05}
mod.jetfuel_pres_con = pe.Constraint(expr=sum(vape[i] * mod.qty['%sjf' % i] for i in vape.keys()) - mod.qty['jf']<= 0)

profit = {'pmf': 700, 'rmf': 600, 'jf': 400, 'fo': 350, 'lbo': 150}
mod.objective = pe.Objective(rule=sum(mod.qty[pr] * profit[pr] for pr in profit.keys()), sense=pe.maximize)
results, log_fpath = run_solver(mod)
# print(results)

# display output
for v in mod.component_objects(pe.Var, active=True):
    print ("Variable component object",v)
    for index in v:
        print ("   ", index, v[index].value)
