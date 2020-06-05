# problem 3
from pyomo import environ as pe
from pyomo.version.info import version_info as pyomoversion
from itertools import product
"""
An engineering factory makes seven products (PROD 1 to PROD 7) on the
following machines: four grinders, two vertical drills, three horizontal drills, one
borer and one planer
"""
items = ['p1', 'p2', 'p3', 'p4', 'p5', 'p6', 'p7']
months = ['jan', 'feb', 'mar', 'apr', 'may', 'jun']
pr_mon = [a + '_' + b for a, b in product(items, months)]
ngrinders = 4
nvertical_drill = 2
nhorizontal_drill = 3
nborer = 1
nplanar = 1

model = pe.ConcreteModel()
# quantity of products that are to be produced for maximizing profits
model.qty = pe.Var(items, months, initialize=0, within=pe.NonNegativeIntegers)
# [Contribution_to_profit, Grinding, Vertical drilling, Horizontal drilling, Boring, Planing]
#               c2p, gr, vd, hd, bo, pl
manuf_costs = [[10, 0.5, 0.1, 0.2, 0.05, 0], # p1
               [6, 0.7, 0.2, 0, 0.03, 0], # p2
               [8, 0, 0, 0.8, 0, 0.01], # p3
               [4, 0, 0.3, 0, 0.07, 0], # p4
               [11, 0.3, 0, 0, 0.1, 0.05], # p5
               [9, 0.2, 0.6, 0, 0, 0], # p6
               [3, 0.5, 0, 0.6, 0.08, 0.05] # p7
               ]
"""
#               p1,  p2,   p3,  p4,  p5,  p6, p7
market_limits_monthwise = {
    'jan': [500, 1000, 300, 300, 800, 200, 100],
    'feb': [600, 500, 200, 0, 400, 300, 150],
    'mar': [300, 600, 0, 0, 500, 400, 100],
    'apr': [200, 300, 400, 500, 200, 0, 100],
    'may': [0, 100, 500, 100, 1000, 300, 0],
    'jun': [500, 500, 100, 300, 1100, 500, 60]
}
"""
#                       jan, feb, mar,apr, may, jun
market_limits = {'p1': [500, 600, 300, 200, 0, 500],
                 'p2': [1000, 500, 600, 300, 100, 500],
                 'p3': [300, 200, 0, 400, 500, 100],
                 'p4': [300, 0, 0, 500, 100, 300],
                 'p5': [800, 400, 500, 200, 1000, 1100],
                 'p6': [200, 300, 400, 0, 300, 500],
                 'p7': [100, 150, 100, 100, 0, 60]}
"""
Each product yields a certain contribution to profit (defined as £/unit selling price minus cost of raw materials).
These quantities (in £/unit) together with the unit production times (hours) required on each process are given below.
A dash indicates that a product does not require a process.
"""
"""
machines down for maintenance month wise
January		1 Grinder
February	2 Horizontal drills
March 		1 Borer
April 		1 Vertical drill
May 		1 Grinder and 1 Vertical drill
June 		1 Planer and 1 Horizontal drill
"""


"""
storage cost 0.5 dollar per unit.
max storage capacity per month per product type =100
january zero stock of [p1...p7]
but end of june stock is 50 units per product.
"""

"""
working days: 6
working hours : 8,
number of shifts : 2
N.B. It may be assumed that each month consists of only 24 working days
"""

"""
No sequencing problems need to be considered.
"""


"""
Objective:
When and what should the factory make in order to maximise the total profit?
Also recommend any price increases and the value of acquiring any new machines.
"""
