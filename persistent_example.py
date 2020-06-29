# persistent solver
# Suppose we want to know how the cost changes as we increase the number of warehouses built.
# warehouse_location.py: Warehouse location determination problem.
# https://pyomo.readthedocs.io/en/stable/advanced_topics/persistent_solvers.html?highlight=persistent%20solver

from pyomo.environ import *
from pyomo.bilevel import *
from commons import *

model = ConcreteModel(name="(WL)")
W = ['Harlingen', 'Memphis', 'Ashland']
C = ['NYC', 'LA', 'Chicago', 'Houston']
d = {('Harlingen', 'NYC'): 1956,
	('Harlingen', 'LA'): 1606,
	('Harlingen', 'Chicago'): 1410,
	('Harlingen', 'Houston'): 330,
	('Memphis', 'NYC'): 1096,
	('Memphis', 'LA'): 1792,
	('Memphis', 'Chicago'): 531,
	('Memphis', 'Houston'): 567,
	('Ashland', 'NYC'): 485,
	('Ashland', 'LA'): 2322,
	('Ashland', 'Chicago'): 324,
	('Ashland', 'Houston'): 1236}

P = 2
model.x = Var(W, C, bounds=(0,1))
model.y = Var(W, within=Binary)

def obj_rule(m):
    return sum(d[w,c]*m.x[w,c] for w in W for c in C)
model.obj = Objective(rule=obj_rule)

def one_per_cust_rule(m, c):
    return sum(m.x[w,c] for w in W) == 1
model.one_per_cust = Constraint(C, rule=one_per_cust_rule)

def warehouse_active_rule(m, w, c):
    return m.x[w,c] <= m.y[w]
model.warehouse_active = Constraint(W, C, rule=warehouse_active_rule)

def num_warehouses_rule(m):
    return sum(m.y[w] for w in W) <= P

model.num_warehouses = Constraint(rule=num_warehouses_rule)
opt = SolverFactory('gurobi_persistent')
opt.set_instance(model)
# model.pprint()

t0 = time.time()
P_list = list(range(1, N_locations+1))
obj_list = []
for p in P_list:
    opt.remove_constraint(model.num_warehouses)
    model.P.value = p
    opt.add_constraint(model.num_warehouses)
    res = opt.solve(load_solutions=False, save_results=False)
    obj_list.append(res.problem.upper_bound)

t1 = time.time()
print(t1-t0)
plt.plot(P_list, obj_list)
plt.show()
