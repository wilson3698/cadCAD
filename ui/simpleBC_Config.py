from engine.utils import bound_norm_random, ep_time_step, env_proc

import numpy as np
from decimal import Decimal

alpha = Decimal('.7') #forgetting param
theta = Decimal('.75') #weight param for rational price
beta = Decimal('0.5') #agant response gain
gamma = Decimal('.03') #action friction param
delta = Decimal('.3') #bounds on price change
omega = Decimal('.5') #bound on burn frac per period

seed = {
    'z': np.random.RandomState(1),
    'a': np.random.RandomState(2),
    'b': np.random.RandomState(3),
    'c': np.random.RandomState(3)
}

# Behaviors per Mechanism

#arbit X Bond
def b1m1(step, sL, s):
    #returns "delta p"
    if s['Price']< s['Pool']/s['Supply']-gamma:
        #print('arbit bond')
        #print((s['Pool']/s['Supply']-s['Price'])/s['Price']*s['Pool']*beta)
        return  (s['Pool']/s['Supply']-s['Price'])/s['Price']*s['Pool']*beta
    else :
        return 0
    

#invest X Bond
def b2m1(step, sL, s):
    #returns "delta p"
    if s['Price']< s['Belief']:
        #print('invest bond')
        #print((s['Belief']-s['Price'])/s['Price']*s['Pool']*beta)
        return  s['Pool']*(s['Belief']-s['Price'])/s['Price']*beta
    else :
        return 0

#arbit X Burn
def b1m2(step, sL, s):
    #returns "delta s"
    if Decimal('1')/s['Price']< s['Supply']/s['Pool']-gamma:
        #print('arbit burn')
        #print((s['Supply']/s['Pool']-Decimal('1')/s['Price'])*s['Price']*s['Supply']*beta)
        return  s['Price']*(s['Supply']/s['Pool']-Decimal('1')/s['Price'])*s['Supply']*beta
    else :
        return 0

#invest X Burn 
def b2m2(step, sL, s):
    #returns "delta s"
    if Decimal('1')/s['Belief']< Decimal('1')/s['Price']:
        #print('invest burn')
        #print(np.min([ s['Pool']*(Decimal('1')/s['Price']-Decimal('1')/s['Belief'])*beta, omega*s['Supply']]))
        return  np.min([ s['Pool']*(Decimal('1')/s['Price']-Decimal('1')/s['Belief'])*beta, omega*s['Supply']])
    else :
        return 0

#
#def b1m3(step, sL, s):
#    return s['s1']
#def b2m3(step, sL, s):
#    return s['s2']


# Internal States per Mechanism

#Pool X Bond
def s1m1(step, sL, s, _input):
    #_input = "delta p"
    return ('Pool',s['Pool']+_input)
    #print("Pool="+str(s['Pool']))

#Supply X Bond     
def s2m1(step, sL, s, _input):
    #_input = "delta p"
    return ('Supply', s['Supply']+ _input*s['Supply']/s['Pool'] )
    #print("Supply="+str(s['Supply']))

# Pool X Burn   
def s1m2(step, sL, s, _input):
    #_input is "delta s"
    return ('Pool',s['Pool']- _input*s['Pool']/s['Supply'])
    #print("Pool="+str(s['Pool']))

# Supply X Burn    
def s2m2(step, sL, s, _input):
    return ('Supply',s['Supply'] - _input)
    #print("Supply="+str(s['Supply']))

#def s1m3(step, sL, s, _input):
#    s['s1'] = s['s1']+Decimal(.25)*(s['s2']-s['s1']) + Decimal(.25)*(_input-s['s1'])
#
#def s2m3(step, sL, s, _input):
#    s['s2'] = s['s2']+Decimal(.25)*(s['s1']-s['s2']) + Decimal(.25)*(_input-s['s2'])

# Exogenous States
proc_one_coef_A = -delta
proc_one_coef_B = delta
def es3p1(step, sL, s, _input):
    rv = bound_norm_random(seed['a'], proc_one_coef_A, proc_one_coef_B)
    return ('Price', theta*s['Price'] * (Decimal('1')+rv) +(Decimal('1')-theta)*s['Pool']/s['Supply'] )
def es4p2(step, sL, s, _input):
    return ('Belief', alpha*s['Belief']+s['Pool']/s['Supply']*(Decimal('1')-alpha))

def es5p2(step, sL, s, _input): # accept timedelta instead of timedelta params
    return ('timestamp', ep_time_step(s, s['timestamp'], seconds=1))

# Environment States
#from numpy.random import randn as rn
def env_a(x):
    return 3
def env_b(x):
    return 7
# def what_ever(x):
#     return x + 1

# Genesis States
state_dict = {
    'Pool': Decimal(10.0),
    'Supply': Decimal(5.0),
    'Price': Decimal(.01),
    'Belief': Decimal(10.0),
    'timestamp': '2018-10-01 15:16:24'
}

exogenous_states = {
    "Price": es3p1,
    "Belief": es4p2,
    "timestamp": es5p2
}

env_processes = {
    "Price": env_proc('2018-10-01 15:16:25', env_a),
    "Belief": env_proc('2018-10-01 15:16:25', env_b)
}

# test return vs. non-return functions as lambdas
# test fully defined functions
mechanisms = {
    "bond": {
        "behaviors": {
            "arbit": b1m1, # lambda step, sL, s: s['s1'] + 1,
            "invest": b2m1
        },
        "states": {
            "Pool": s1m1,
            "Supply": s2m1,
        }
    },
    "burn": {
        "behaviors": {
            "arbit": b1m2,
            "invest": b2m2
        },
        "states": {
            "Pool": s1m2,
            "Supply": s2m2,
        }
    },
#    "m3": {
#        "behaviors": {
#            "b1": b1m3,
#            "b2": b2m3
#        },
#        "states": {
#            "s1": s1m3,
#            "s2": s2m3,
#        }
#    }
}

sim_config = {
    "N": 1,
    "R": 1000
}