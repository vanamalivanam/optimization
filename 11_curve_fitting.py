#!/usr/bin/env python
import numpy as np
import cvxpy as cp
print('installed solvers:', cp.installed_solvers())

pts = [(0, 1), (0.5, 0.9), (1, 0.7), (1.5, 1.5), (1.9, 2), (2.5, 2.4), (3, 3.2), (3.5, 2), (4, 2.7), (4.5, 3.5),
       (5, 1), (5.5, 4), (6, 3.6), (6.6, 2.7), (7, 5.7), (7.6, 4.6), (8.5, 6), (9, 6.8), (10, 7.3)]
xset, yset = zip(*pts)
num_pts = len(pts)

# linear 
# y = bx + a
# abs(y_i - b*x_i - a)
var = cp.Variable(2, name='ba')
abserr = np.sum(cp.norm1(yset - var[0]*xset - num_pts*var[1]))
objective = cp.Minimize(abserr)
model = cp.Problem(objective)
try:
    objective_value = model.solve(solver=cp.CBC, verbose=True)
    print('objective value', objective_value)
except cp.error.SolverError as e:
    print('solver not found', e)
print('value of b', var[0].value)
print('value of a', var[1].value)


# quadratic
# y = cx2 + bx + a
print('solving quadratic functions')
var = cp.Variable(3, name='cba')
abserr = cp.sum(cp.norm1(yset - var[0]*xset*xset - var[1]*xset - var[2]))
objective = cp.Minimize(abserr)
model = cp.Problem(objective)

try:
    objective_value = model.solve(solver=cp.CBC, verbose=True)
    print('objective value', objective_value)
except cp.error.SolverError as e:
    print('solver not found', e)

print('value of c', var[0].value)
print('value of b', var[1].value)
print('value of a', var[2].value)
