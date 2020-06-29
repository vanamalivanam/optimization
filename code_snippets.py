def create_vars():
    # create decision variables
    S = streams.keys()
    P = products.keys()
    m.x = pyomo.Var(S,P, domain=pyomo.NonNegativeReals)

    # another style of writing objective
    revenue = sum(sum(m.x[s,p]*products[p]['price'] for s in S) for p in P)
    cost = sum(sum(m.x[s,p]*streams[s]['cost'] for s in S) for p in P)
    m.profit = pyomo.Objective(expr = revenue - cost, sense=pyomo.maximize)

def unit_commitment():
    m = pyo.ConcreteModel()
    m.N = pyo.Set(initialize=N)
    m.T = pyo.Set(initialize=T)

    m.x = pyo.Var(m.N, m.T, bounds = (0, pmax))
    m.u = pyo.Var(m.N, m.T, domain=pyo.Binary)
    # objective
    m.cost = pyo.Objective(expr = sum(m.x[n,t]*a[n] + m.u[n,t]*b[n] for t in m.T for n in m.N), sense=pyo.minimize)

    # demand
    m.demand = pyo.Constraint(m.T, rule=lambda m, t: sum(m.x[n,t] for n in N) == d[t])

    # semi-continuous
    m.lb = pyo.Constraint(m.N, m.T, rule=lambda m, n, t: pmin*m.u[n,t] <= m.x[n,t])
    m.ub = pyo.Constraint(m.N, m.T, rule=lambda m, n, t: pmax*m.u[n,t] >= m.x[n,t])
    pyo.SolverFactory('cbc').solve(m).write()
