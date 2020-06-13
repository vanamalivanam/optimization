#!/usr/bin/env python
from commons import *

skilltype = ['semi', 'skilled', 'unskilled']
req = {'current': {'semi': 1500, 'skilled': 1000, 'unskilled': 2000},
       'year_1': {'semi': 1400, 'skilled': 1000, 'unskilled': 1000},
       'year_2': {'semi': 2000, 'skilled': 1500, 'unskilled': 500},
       'year_3': {'semi': 2500, 'skilled': 2000, 'unskilled': 0}
       }
fallout_rate = {'less_than_year_percent': {'semi': 20, 'skilled': 10, 'unskilled': 25},
                'more_than_year_percent': {'semi': 5, 'skilled': 5, 'unskilled': 10}
                }

#  it will be assumed that everything happens on the first day of each year.
# Owing to the installation of new machinery, fewer unskilled but more skilled and semi-skilled workers will be
# required. In addition to this, a downturn in trade is expected in the next year, which will reduce the need for
# workers in all categories. The estimated manpower requirements for the next three years are as follows:

# constraint 1: recruitment
recruit= {'semi':800, 'skilled':500, 'unskilled':500}

# constraints 2 : retraining
# It is possible to retrain up to 200 unskilled workers per year to make them semiskilled. This costs £400 per worker.
# The retraining of semi-skilled workers to make them skilled is limited to no more than one quarter of the skilled
# labour force at the time as some training is done on the job. Retraining a semi-skilled worker in this way costs £500
cost_unsk_semi = 400
num_unsk_to_semi <= 200
num_semi_to_skl <= num_skl/4.0
cost_semi_skl = 500

# Downgrading of workers to a lower skill is possible but 50% of such workers leave, although it costs the company
# nothing. (This wastage is additional to the ‘natural wastage’ described above).


# constraint 3: redundancy

# constraint 5: overmanning
# It is possible to employ up to 150 more workers over the whole company than
# are needed, but the extra costs per employee per year are as follows:
overmanning_cost = {'unskilled':1500, 'semi':2000, 'skilled':3000}

# constraint 5: short time working
# Up to 50 workers in each category of skill can be put on short-time working.
# The cost of this (per employee per year) is as follows:
# An employee on short-time working meets the production requirements of half a full-time employee.
cost_short_term = {'unskilled':500, 'semi':400, 'skilled':400}



# The company’s declared objective is to minimise redundancy. How should they operate in order to do this?
# If their policy were to minimise costs, how much extra would this save?
# Deduce the cost of saving each type of job each year.