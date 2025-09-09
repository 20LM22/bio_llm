from lark import Lark
from stl_example_generator import STLBase
import json, re, pickle, math, random

####################################################################################
# Debugging logging
####################################################################################

import logging

####################################################################################
# Set up structures, parameters
####################################################################################

file_name = f'../config/config_v4.json'

with open(file_name, 'r') as f:
    params = json.load(f)

stl_base_instance = STLBase()

grammar = params['grammar']
parser = Lark(grammar)

def check_time_intervals(sample):
    # also check for ranges time interval
    time_interval_num_num = r'\[\d+,\d+\]'
    time_interval_inf_num = r'\[∞,\d+\]'
    time_interval_inf_inf = r'\[∞,∞\]'

    if len(re.findall(time_interval_inf_inf, sample)) > 0 or len(re.findall(time_interval_inf_num, sample)) > 0:
        return False
    
    intervals = re.findall(time_interval_num_num, sample)    
    if intervals is not None:
        print("there are intervals")
        for interval in intervals:
            print(f"interval: {interval}")
            t_a = interval.split(',')[0][1:]
            t_b = interval.split(',')[1][:-1]
            print(f't_a: {t_a}')
            print(f't_b: {t_b}')
            if int(t_b) <= int(t_a):
                return False
    return True

# Large 5K dataset
large_dataset = []

# Obtain 5K samples
for i in range(5000):
    a = stl_base_instance.sample('omega')
    while len(a) > 90 or check_time_intervals(a) is False:
        a = stl_base_instance.sample('omega')
    print(f'a: {a}')
    large_dataset.append(a)

# From the 5K samples, create curated dataset with desired percentages

curated_size = 300 # could put this small exercise into the paper - sampling w/ or w/o replacement
curated_arr = []
curated = False

# First determine the size of each bucket
non_temporal_samples = int(math.floor(0.3 * curated_size))

# print(f'non_temporal_samples: {non_temporal_samples}')

non_temporal_u = math.floor(0.2 * non_temporal_samples)
# print(f'non_temporal_u: {non_temporal_u}')

# print(f'non temporal u: {non_temporal_u}')
non_temporal_u_and_u = int(math.floor(0.3 * non_temporal_samples))
# print(f'non temporal u and u: {non_temporal_u_and_u}')
non_temporal_u_implies_u = non_temporal_samples - non_temporal_u - non_temporal_u_and_u
# print(f'non temporal u implies u: {non_temporal_u_implies_u}')

# These are the smallest non-temporal buckets
non_temporal_u_gt = non_temporal_u_lt = non_temporal_u_eq = non_temporal_u_d_gt = non_temporal_u_d_lt = non_temporal_u_d_eq = int(non_temporal_u / 5)
non_temporal_u_and_u_gt = non_temporal_u_and_u_lt = non_temporal_u_and_u_eq = non_temporal_u_and_u_d_gt = non_temporal_u_and_u_d_lt = non_temporal_u_and_u_d_eq = int(non_temporal_u_and_u / 5)
non_temporal_u_implies_u_gt = non_temporal_u_implies_u_lt = non_temporal_u_implies_u_eq = non_temporal_u_implies_u_d_gt = non_temporal_u_implies_u_d_lt = non_temporal_u_implies_u_d_eq = int(non_temporal_u_implies_u / 5)

# Create temporal buckets
temporal_samples = curated_size - non_temporal_samples

t_psi_implies_psi = int(math.floor(0.15 * temporal_samples))
t_omega_and_omega = int(math.floor(0.30 * temporal_samples))
t_psi = temporal_samples - t_psi_implies_psi - t_omega_and_omega

# Each one with the psi's should have equal number of temporal operators
t_psi_implies_psi_fg = t_psi_implies_psi_f = t_psi_implies_psi_g = int(t_psi_implies_psi / 3)
t_omega_and_omega_fg = t_omega_and_omega_f = t_omega_and_omega_g = int(t_omega_and_omega / 3)
t_psi_fg = t_psi_f = t_psi_g = int(t_psi / 3)

# Need to break into a u implies u, u and u, regular u
t_psi_implies_psi_fg_u_implies_u = int(math.floor(0.25 * t_psi_implies_psi_fg))
t_psi_implies_psi_fg_u_and_u = int(math.floor(0.25 * t_psi_implies_psi_fg))
t_psi_implies_psi_fg_u = t_psi_implies_psi_fg - t_psi_implies_psi_fg_u_implies_u - t_psi_implies_psi_fg_u_and_u

t_psi_implies_psi_f_u_implies_u = int(math.floor(0.25 * t_psi_implies_psi_f))
t_psi_implies_psi_f_u_and_u = int(math.floor(0.25 * t_psi_implies_psi_f))
t_psi_implies_psi_f_u = t_psi_implies_psi_f - t_psi_implies_psi_f_u_implies_u - t_psi_implies_psi_f_u_and_u

t_psi_implies_psi_g_u_implies_u = int(math.floor(0.25 * t_psi_implies_psi_g))
t_psi_implies_psi_g_u_and_u = int(math.floor(0.25 * t_psi_implies_psi_g))
t_psi_implies_psi_g_u = t_psi_implies_psi_g - t_psi_implies_psi_g_u_implies_u - t_psi_implies_psi_g_u_and_u

#--

t_omega_and_omega_fg_u_implies_u = int(math.floor(0.25 * t_omega_and_omega_fg))
t_omega_and_omega_fg_u_and_u = int(math.floor(0.25 * t_omega_and_omega_fg))
t_omega_and_omega_fg_u = t_omega_and_omega_fg - t_omega_and_omega_fg_u_implies_u - t_omega_and_omega_fg_u_and_u

t_omega_and_omega_f_u_implies_u = int(math.floor(0.25 * t_omega_and_omega_f))
t_omega_and_omega_f_u_and_u = int(math.floor(0.25 * t_omega_and_omega_f))
t_omega_and_omega_f_u = t_omega_and_omega_f - t_omega_and_omega_f_u_implies_u - t_omega_and_omega_f_u_and_u

t_omega_and_omega_g_u_implies_u = int(math.floor(0.25 * t_omega_and_omega_g))
t_omega_and_omega_g_u_and_u = int(math.floor(0.25 * t_omega_and_omega_g))
t_omega_and_omega_g_u = t_omega_and_omega_g - t_omega_and_omega_g_u_implies_u - t_omega_and_omega_g_u_and_u

#--

t_psi_fg_u_implies_u = int(math.floor(0.25 * t_psi_fg))
t_psi_fg_u_and_u = int(math.floor(0.25 * t_psi_fg))
t_psi_fg_u = t_psi_fg - t_psi_fg_u_implies_u - t_psi_fg_u_and_u

t_psi_f_u_implies_u = int(math.floor(0.25 * t_psi_f))
t_psi_f_u_and_u = int(math.floor(0.25 * t_psi_f))
t_psi_f_u = t_psi_f - t_psi_f_u_implies_u - t_psi_f_u_and_u

t_psi_g_u_implies_u = int(math.floor(0.25 * t_psi_g))
t_psi_g_u_and_u = int(math.floor(0.25 * t_psi_g))
t_psi_g_u = t_psi_g - t_psi_g_u_implies_u - t_psi_g_u_and_u

# - - - - - - - - - - -- - - -  - --- - - -  - - - - -- - - - - - - - -  -- - - - - - - - - - 
"""
print(f'non temporal u gt: {non_temporal_u_gt}')
print(f'non temporal u lt: {non_temporal_u_lt}')
print(f'non temporal u eq: {non_temporal_u_eq}')
print(f'non temporal u d_gt: {non_temporal_u_d_gt}')
print(f'non temporal u d_lt: {non_temporal_u_d_lt}')
print(f'non temporal u d_eq: {non_temporal_u_d_eq}\n')

print(f'non temporal u and u gt: {non_temporal_u_and_u_gt}')
print(f'non temporal u and u lt: {non_temporal_u_and_u_lt}')
print(f'non temporal u and u eq: {non_temporal_u_and_u_eq}')
print(f'non temporal u and u d_gt: {non_temporal_u_and_u_d_gt}')
print(f'non temporal u and u d_lt: {non_temporal_u_and_u_d_lt}')
print(f'non temporal u and u d_eq: {non_temporal_u_and_u_d_eq}\n')

print(f'non temporal u implies u gt: {non_temporal_u_implies_u_gt}')
print(f'non temporal u implies u lt: {non_temporal_u_implies_u_lt}')
print(f'non temporal u implies u eq: {non_temporal_u_implies_u_eq}')
print(f'non temporal u implies u d_gt: {non_temporal_u_implies_u_d_gt}')
print(f'non temporal u implies u d_lt: {non_temporal_u_implies_u_d_lt}')
print(f'non temporal u implies u d_eq: {non_temporal_u_implies_u_d_eq}\n')

print(f'temporal psi implies psi fg u implies u: {t_psi_implies_psi_fg_u_implies_u}')
print(f'temporal psi implies psi fg u and u: {t_psi_implies_psi_fg_u_and_u}')
print(f'temporal psi implies psi fg u: {t_psi_implies_psi_fg_u}\n')

print(f'temporal psi implies psi f u implies u: {t_psi_implies_psi_f_u_implies_u}')
print(f'temporal psi implies psi f u and u: {t_psi_implies_psi_f_u_and_u}')
print(f'temporal psi implies psi f u: {t_psi_implies_psi_f_u}\n')

print(f'temporal psi implies psi g u implies u: {t_psi_implies_psi_g_u_implies_u}')
print(f'temporal psi implies psi g u and u: {t_psi_implies_psi_g_u_and_u}')
print(f'temporal psi implies psi g u: {t_psi_implies_psi_g_u}\n')

print(f'temporal omega and omega fg u implies u: {t_omega_and_omega_fg_u_implies_u}')
print(f'temporal omega and omega fg u and u: {t_omega_and_omega_fg_u_and_u}')
print(f'temporal omega and omega fg u: {t_omega_and_omega_fg_u}\n')

print(f'temporal omega and omega f u implies u: {t_omega_and_omega_f_u_implies_u}')
print(f'temporal omega and omega f u and u: {t_omega_and_omega_f_u_and_u}')
print(f'temporal omega and omega f u: {t_omega_and_omega_f_u}\n')

print(f'temporal omega and omega g u implies u: {t_omega_and_omega_g_u_implies_u}')
print(f'temporal omega and omega g u and u: {t_omega_and_omega_g_u_and_u}')
print(f'temporal omega and omega g u: {t_omega_and_omega_g_u}\n')

print(f'temporal psi fg u implies u: {t_psi_fg_u_implies_u}')
print(f'temporal psi fg u and u: {t_psi_fg_u_and_u}')
print(f'temporal psi fg u: {t_psi_fg_u}\n')

print(f'temporal psi f u implies u: {t_psi_f_u_implies_u}')
print(f'temporal psi f u and u: {t_psi_f_u_and_u}')
print(f'temporal psi f u: {t_psi_f_u}\n')

print(f'temporal psi g u implies u: {t_psi_g_u_implies_u}')
print(f'temporal psi g u and u: {t_psi_g_u_and_u}')
print(f'temporal psi g u: {t_psi_g_u}\n')

p = 5/0
"""

#  - - - - -- - - - -  - - -  - - - - - - - - - - - - - - - - - - - - - - - - - -- - - - -- - 

# Each of those 9 categories for the 4 types needs to be split into 6 ways for each of the operators --> Break each into all 6 operators, just do this in the generation

# Then sample to fill each bucket, checking that the samples fulfill the bucket requirements before adding them
print("starting1")
curated = False
for i in range(non_temporal_u_gt):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if (len(re.findall(r'temp_op_fg',tree))==0 and len(re.findall(r'temp_op_f',tree))==0 and len(re.findall(r'temp_op_g',tree))==0) and len(re.findall(r"'RULE', 'gt'",tree))>0:
            # count it
            curated_arr.append(res)
            curated = True
print("ending1")
for i in range(non_temporal_u_lt):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if (len(re.findall(r'temp_op_fg',tree))==0 and len(re.findall(r'temp_op_f',tree))==0 and len(re.findall(r'temp_op_g',tree))==0) and len(re.findall(r"'RULE', 'lt'",tree))>0:
            # count it
            curated_arr.append(res)
            curated = True

for i in range(non_temporal_u_eq):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if (len(re.findall(r'temp_op_fg',tree))==0 and len(re.findall(r'temp_op_f',tree))==0 and len(re.findall(r'temp_op_g',tree))==0) and len(re.findall(r"'RULE', 'eq'",tree))>0:
            # count it
            curated_arr.append(res)
            curated = True
"""
for i in range(non_temporal_u_d_gt):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if (len(re.findall(r'temp_op_fg',tree))==0 and len(re.findall(r'temp_op_f',tree))==0 and len(re.findall(r'temp_op_g',tree))==0) and len(re.findall(r"'RULE', 'd_gt'",tree))>0:
            # count it
            curated_arr.append(res)
            curated = True
"""
for i in range(non_temporal_u_d_lt):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if (len(re.findall(r'temp_op_fg',tree))==0 and len(re.findall(r'temp_op_f',tree))==0 and len(re.findall(r'temp_op_g',tree))==0) and len(re.findall(r"'RULE', 'd_lt'",tree))>0:
            # count it
            curated_arr.append(res)
            curated = True

for i in range(non_temporal_u_d_eq):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if (len(re.findall(r'temp_op_fg',tree))==0 and len(re.findall(r'temp_op_f',tree))==0 and len(re.findall(r'temp_op_g',tree))==0) and len(re.findall(r"'RULE', 'd_eq'",tree))>0:
            # count it
            curated_arr.append(res)
            curated = True

#--
print("starting 2")
for i in range(non_temporal_u_and_u_gt):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if (len(re.findall(r'temp_op_fg',tree))==0 and len(re.findall(r'temp_op_f',tree))==0 and len(re.findall(r'temp_op_g',tree))==0) and len(re.findall(r"'RULE', 'gt'",tree))>0 and len(re.findall(r"u_and_u",tree))>0:
            # count it
            curated_arr.append(res)
            curated = True

for i in range(non_temporal_u_and_u_lt):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if (len(re.findall(r'temp_op_fg',tree))==0 and len(re.findall(r'temp_op_f',tree))==0 and len(re.findall(r'temp_op_g',tree))==0) and len(re.findall(r"'RULE', 'lt'",tree))>0 and len(re.findall(r"u_and_u",tree))>0:
            # count it
            curated_arr.append(res)
            curated = True

for i in range(non_temporal_u_and_u_eq):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if (len(re.findall(r'temp_op_fg',tree))==0 and len(re.findall(r'temp_op_f',tree))==0 and len(re.findall(r'temp_op_g',tree))==0) and len(re.findall(r"'RULE', 'eq'",tree))>0 and len(re.findall(r"u_and_u",tree))>0:
            # count it
            curated_arr.append(res)
            curated = True

for i in range(non_temporal_u_and_u_d_gt):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if (len(re.findall(r'temp_op_fg',tree))==0 and len(re.findall(r'temp_op_f',tree))==0 and len(re.findall(r'temp_op_g',tree))==0) and len(re.findall(r"'RULE', 'd_gt'",tree))>0 and len(re.findall(r"u_and_u",tree))>0:
            # count it
            curated_arr.append(res)
            curated = True
"""
for i in range(non_temporal_u_and_u_d_lt):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if (len(re.findall(r'temp_op_fg',tree))==0 and len(re.findall(r'temp_op_f',tree))==0 and len(re.findall(r'temp_op_g',tree))==0) and len(re.findall(r"'RULE', 'd_lt'",tree))>0 and len(re.findall(r"u_and_u",tree))>0:
            # count it
            curated_arr.append(res)
            curated = True
"""
for i in range(non_temporal_u_and_u_d_eq):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if (len(re.findall(r'temp_op_fg',tree))==0 and len(re.findall(r'temp_op_f',tree))==0 and len(re.findall(r'temp_op_g',tree))==0) and len(re.findall(r"'RULE', 'd_eq'",tree))>0 and len(re.findall(r"u_and_u",tree))>0:
            # count it
            curated_arr.append(res)
            curated = True

# -- 
print("starting 3")
for i in range(non_temporal_u_implies_u_gt):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if (len(re.findall(r'temp_op_fg',tree))==0 and len(re.findall(r'temp_op_f',tree))==0 and len(re.findall(r'temp_op_g',tree))==0) and len(re.findall(r"'RULE', 'gt'",tree))>0 and len(re.findall(r"u_implies_u",tree))>0:
            # count it
            curated_arr.append(res)
            curated = True

for i in range(non_temporal_u_implies_u_lt):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if (len(re.findall(r'temp_op_fg',tree))==0 and len(re.findall(r'temp_op_f',tree))==0 and len(re.findall(r'temp_op_g',tree))==0) and len(re.findall(r"'RULE', 'lt'",tree))>0 and len(re.findall(r"u_implies_u",tree))>0:
            # count it
            curated_arr.append(res)
            curated = True

for i in range(non_temporal_u_implies_u_eq):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if (len(re.findall(r'temp_op_fg',tree))==0 and len(re.findall(r'temp_op_f',tree))==0 and len(re.findall(r'temp_op_g',tree))==0) and len(re.findall(r"'RULE', 'eq'",tree))>0 and len(re.findall(r"u_implies_u",tree))>0:
            # count it
            curated_arr.append(res)
            curated = True

for i in range(non_temporal_u_implies_u_d_gt):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if (len(re.findall(r'temp_op_fg',tree))==0 and len(re.findall(r'temp_op_f',tree))==0 and len(re.findall(r'temp_op_g',tree))==0) and len(re.findall(r"'RULE', 'd_gt'",tree))>0 and len(re.findall(r"u_implies_u",tree))>0:
            # count it
            curated_arr.append(res)
            curated = True

for i in range(non_temporal_u_implies_u_d_lt):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if (len(re.findall(r'temp_op_fg',tree))==0 and len(re.findall(r'temp_op_f',tree))==0 and len(re.findall(r'temp_op_g',tree))==0) and len(re.findall(r"'RULE', 'd_lt'",tree))>0 and len(re.findall(r"u_implies_u",tree))>0:
            # count it
            curated_arr.append(res)
            curated = True
"""
for i in range(non_temporal_u_implies_u_d_eq):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if (len(re.findall(r'temp_op_fg',tree))==0 and len(re.findall(r'temp_op_f',tree))==0 and len(re.findall(r'temp_op_g',tree))==0) and len(re.findall(r"'RULE', 'd_eq'",tree))>0 and len(re.findall(r"u_implies_u",tree))>0:
            # count it
            curated_arr.append(res)
            curated = True
"""
#-- done with non-temporal
#-- beginning of singular temporal psi
print("starting 4")
# fg
for i in range(int(t_psi_fg_u_implies_u/5)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_fg',tree))>0 and len(re.findall(r"u_implies_u",tree))>0 and len(re.findall(r"'RULE', 'gt'",tree)) and len(re.findall(r"omega_and_omega",tree))==0 and len(re.findall(r"psi_implies_psi",tree))==0:
            curated_arr.append(res)
            curated = True
for i in range(int(t_psi_fg_u_implies_u/5)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_fg',tree))>0 and len(re.findall(r"u_implies_u",tree))>0 and len(re.findall(r"'RULE', 'lt'",tree)) and len(re.findall(r"omega_and_omega", tree))==0 and len(re.findall(r"psi_implies_psi", tree))==0:
            curated_arr.append(res)
            curated = True
for i in range(int(t_psi_fg_u_implies_u/5)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_fg',tree))>0 and len(re.findall(r"u_implies_u",tree))>0 and len(re.findall(r"'RULE', 'eq'",tree)) and len(re.findall(r'omega_and_omega', tree))==0 and len(re.findall(r'psi_implies_psi', tree))==0:
            curated_arr.append(res)
            curated = True
"""for i in range(int(t_psi_fg_u_implies_u/6)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_fg',tree))>0 and len(re.findall(r"u_implies_u",tree))>0 and len(re.findall(r"'RULE', 'd_gt'",tree)) and len(re.findall(r'omega_and_omega', tree))==0 and len(re.findall(r'psi_implies_psi', tree))==0:
            curated_arr.append(res)
            curated = True """
for i in range(int(t_psi_fg_u_implies_u/5)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_fg',tree))>0 and len(re.findall(r"u_implies_u",tree))>0 and len(re.findall(r"'RULE', 'd_lt'",tree)) and len(re.findall(r'omega_and_omega', tree))==0 and len(re.findall(r'psi_implies_psi', tree))==0:
            curated_arr.append(res)
            curated = True
for i in range(int(t_psi_fg_u_implies_u/5)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_fg',tree))>0 and len(re.findall(r"u_implies_u",tree))>0 and len(re.findall(r"'RULE', 'd_eq'",tree)) and len(re.findall(r'omega_and_omega', tree))==0 and len(re.findall(r'psi_implies_psi', tree))==0:
            curated_arr.append(res)
            curated = True
# now f
print("printing 5")
for i in range(int(t_psi_f_u_implies_u/5)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_f',tree))>0 and len(re.findall(r"u_implies_u",tree))>0 and len(re.findall(r"'RULE', 'gt'",tree)) and len(re.findall(r"omega_and_omega",tree))==0 and len(re.findall(r"psi_implies_psi",tree))==0:
            curated_arr.append(res)
            curated = True
for i in range(int(t_psi_f_u_implies_u/5)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_f',tree))>0 and len(re.findall(r"u_implies_u",tree))>0 and len(re.findall(r"'RULE', 'lt'",tree)) and len(re.findall(r"omega_and_omega", tree))==0 and len(re.findall(r"psi_implies_psi", tree))==0:
            curated_arr.append(res)
            curated = True
for i in range(int(t_psi_f_u_implies_u/5)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_f',tree))>0 and len(re.findall(r"u_implies_u",tree))>0 and len(re.findall(r"'RULE', 'eq'",tree)) and len(re.findall(r'omega_and_omega', tree))==0 and len(re.findall(r'psi_implies_psi', tree))==0:
            curated_arr.append(res)
            curated = True
for i in range(int(t_psi_f_u_implies_u/5)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_f',tree))>0 and len(re.findall(r"u_implies_u",tree))>0 and len(re.findall(r"'RULE', 'd_gt'",tree)) and len(re.findall(r'omega_and_omega', tree))==0 and len(re.findall(r'psi_implies_psi', tree))==0:
            curated_arr.append(res)
            curated = True
"""for i in range(int(t_psi_f_u_implies_u/5)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_f',tree))>0 and len(re.findall(r"u_implies_u",tree))>0 and len(re.findall(r"'RULE', 'd_lt'",tree)) and len(re.findall(r'omega_and_omega', tree))==0 and len(re.findall(r'psi_implies_psi', tree))==0:
            curated_arr.append(res)
            curated = True"""
for i in range(int(t_psi_f_u_implies_u/5)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_f',tree))>0 and len(re.findall(r"u_implies_u",tree))>0 and len(re.findall(r"'RULE', 'd_eq'",tree)) and len(re.findall(r'omega_and_omega', tree))==0 and len(re.findall(r'psi_implies_psi', tree))==0:
            curated_arr.append(res)
            curated = True
print("starting 6")
# g
for i in range(int(t_psi_g_u_implies_u/5)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_g',tree))>0 and len(re.findall(r"u_implies_u",tree))>0 and len(re.findall(r"'RULE', 'gt'",tree)) and len(re.findall(r"omega_and_omega",tree))==0 and len(re.findall(r"psi_implies_psi",tree))==0:
            curated_arr.append(res)
            curated = True
for i in range(int(t_psi_g_u_implies_u/5)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_g',tree))>0 and len(re.findall(r"u_implies_u",tree))>0 and len(re.findall(r"'RULE', 'lt'",tree)) and len(re.findall(r"omega_and_omega", tree))==0 and len(re.findall(r"psi_implies_psi", tree))==0:
            curated_arr.append(res)
            curated = True
for i in range(int(t_psi_g_u_implies_u/5)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_g',tree))>0 and len(re.findall(r"u_implies_u",tree))>0 and len(re.findall(r"'RULE', 'eq'",tree)) and len(re.findall(r'omega_and_omega', tree))==0 and len(re.findall(r'psi_implies_psi', tree))==0:
            curated_arr.append(res)
            curated = True
for i in range(int(t_psi_g_u_implies_u/5)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_g',tree))>0 and len(re.findall(r"u_implies_u",tree))>0 and len(re.findall(r"'RULE', 'd_gt'",tree)) and len(re.findall(r'omega_and_omega', tree))==0 and len(re.findall(r'psi_implies_psi', tree))==0:
            curated_arr.append(res)
            curated = True
for i in range(int(t_psi_g_u_implies_u/5)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_g',tree))>0 and len(re.findall(r"u_implies_u",tree))>0 and len(re.findall(r"'RULE', 'd_lt'",tree)) and len(re.findall(r'omega_and_omega', tree))==0 and len(re.findall(r'psi_implies_psi', tree))==0:
            curated_arr.append(res)
            curated = True
"""for i in range(int(t_psi_g_u_implies_u/6)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_g',tree))>0 and len(re.findall(r"u_implies_u",tree))>0 and len(re.findall(r"'RULE', 'd_eq'",tree)) and len(re.findall(r'omega_and_omega', tree))==0 and len(re.findall(r'psi_implies_psi', tree))==0:
            curated_arr.append(res)
            curated = True"""
#-------------------------------------------------------------------------------------
print("starting 7")
# fg
for i in range(int(t_psi_fg_u_and_u/5)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_fg',tree))>0 and len(re.findall(r"u_and_u",tree))>0 and len(re.findall(r"'RULE', 'gt'",tree)) and len(re.findall(r"omega_and_omega",tree))==0 and len(re.findall(r"psi_implies_psi",tree))==0:
            curated_arr.append(res)
            curated = True
for i in range(int(t_psi_fg_u_and_u/5)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_fg',tree))>0 and len(re.findall(r"u_and_u",tree))>0 and len(re.findall(r"'RULE', 'lt'",tree)) and len(re.findall(r"omega_and_omega", tree))==0 and len(re.findall(r"psi_implies_psi", tree))==0:
            curated_arr.append(res)
            curated = True
for i in range(int(t_psi_fg_u_and_u/5)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_fg',tree))>0 and len(re.findall(r"u_and_u",tree))>0 and len(re.findall(r"'RULE', 'eq'",tree)) and len(re.findall(r'omega_and_omega', tree))==0 and len(re.findall(r'psi_implies_psi', tree))==0:
            curated_arr.append(res)
            curated = True
"""for i in range(int(t_psi_fg_u_and_u/5)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_fg',tree))>0 and len(re.findall(r"u_and_u",tree))>0 and len(re.findall(r"'RULE', 'd_gt'",tree)) and len(re.findall(r'omega_and_omega', tree))==0 and len(re.findall(r'psi_implies_psi', tree))==0:
            curated_arr.append(res)
            curated = True"""
for i in range(int(t_psi_fg_u_and_u/5)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_fg',tree))>0 and len(re.findall(r"u_and_u",tree))>0 and len(re.findall(r"'RULE', 'd_lt'",tree)) and len(re.findall(r'omega_and_omega', tree))==0 and len(re.findall(r'psi_implies_psi', tree))==0:
            curated_arr.append(res)
            curated = True
for i in range(int(t_psi_fg_u_and_u/5)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_fg',tree))>0 and len(re.findall(r"u_and_u",tree))>0 and len(re.findall(r"'RULE', 'd_eq'",tree)) and len(re.findall(r'omega_and_omega', tree))==0 and len(re.findall(r'psi_implies_psi', tree))==0:
            curated_arr.append(res)
            curated = True
# now f
print("printing 8")
for i in range(int(t_psi_f_u_and_u/5)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_f',tree))>0 and len(re.findall(r"u_and_u",tree))>0 and len(re.findall(r"'RULE', 'gt'",tree)) and len(re.findall(r"omega_and_omega",tree))==0 and len(re.findall(r"psi_implies_psi",tree))==0:
            curated_arr.append(res)
            curated = True
for i in range(int(t_psi_f_u_and_u/5)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_f',tree))>0 and len(re.findall(r"u_and_u",tree))>0 and len(re.findall(r"'RULE', 'lt'",tree)) and len(re.findall(r"omega_and_omega", tree))==0 and len(re.findall(r"psi_implies_psi", tree))==0:
            curated_arr.append(res)
            curated = True
for i in range(int(t_psi_f_u_and_u/5)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_f',tree))>0 and len(re.findall(r"u_and_u",tree))>0 and len(re.findall(r"'RULE', 'eq'",tree)) and len(re.findall(r'omega_and_omega', tree))==0 and len(re.findall(r'psi_implies_psi', tree))==0:
            curated_arr.append(res)
            curated = True
for i in range(int(t_psi_f_u_and_u/5)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_f',tree))>0 and len(re.findall(r"u_and_u",tree))>0 and len(re.findall(r"'RULE', 'd_gt'",tree)) and len(re.findall(r'omega_and_omega', tree))==0 and len(re.findall(r'psi_implies_psi', tree))==0:
            curated_arr.append(res)
            curated = True
"""for i in range(int(t_psi_f_u_and_u/6)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_f',tree))>0 and len(re.findall(r"u_and_u",tree))>0 and len(re.findall(r"'RULE', 'd_lt'",tree)) and len(re.findall(r'omega_and_omega', tree))==0 and len(re.findall(r'psi_implies_psi', tree))==0:
            curated_arr.append(res)
            curated = True"""
for i in range(int(t_psi_f_u_and_u/5)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_f',tree))>0 and len(re.findall(r"u_and_u",tree))>0 and len(re.findall(r"'RULE', 'd_eq'",tree)) and len(re.findall(r'omega_and_omega', tree))==0 and len(re.findall(r'psi_implies_psi', tree))==0:
            curated_arr.append(res)
            curated = True
print("starting 9")
# g
for i in range(int(t_psi_g_u_and_u/5)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_g',tree))>0 and len(re.findall(r"u_and_u",tree))>0 and len(re.findall(r"'RULE', 'gt'",tree)) and len(re.findall(r"omega_and_omega",tree))==0 and len(re.findall(r"psi_implies_psi",tree))==0:
            curated_arr.append(res)
            curated = True
for i in range(int(t_psi_g_u_and_u/5)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_g',tree))>0 and len(re.findall(r"u_and_u",tree))>0 and len(re.findall(r"'RULE', 'lt'",tree)) and len(re.findall(r"omega_and_omega", tree))==0 and len(re.findall(r"psi_implies_psi", tree))==0:
            curated_arr.append(res)
            curated = True
for i in range(int(t_psi_g_u_and_u/5)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_g',tree))>0 and len(re.findall(r"u_and_u",tree))>0 and len(re.findall(r"'RULE', 'eq'",tree)) and len(re.findall(r'omega_and_omega', tree))==0 and len(re.findall(r'psi_implies_psi', tree))==0:
            curated_arr.append(res)
            curated = True
for i in range(int(t_psi_g_u_and_u/5)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_g',tree))>0 and len(re.findall(r"u_and_u",tree))>0 and len(re.findall(r"'RULE', 'd_gt'",tree)) and len(re.findall(r'omega_and_omega', tree))==0 and len(re.findall(r'psi_implies_psi', tree))==0:
            curated_arr.append(res)
            curated = True
for i in range(int(t_psi_g_u_and_u/5)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_g',tree))>0 and len(re.findall(r"u_and_u",tree))>0 and len(re.findall(r"'RULE', 'd_lt'",tree)) and len(re.findall(r'omega_and_omega', tree))==0 and len(re.findall(r'psi_implies_psi', tree))==0:
            curated_arr.append(res)
            curated = True
"""for i in range(int(t_psi_g_u_and_u/6)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_g',tree))>0 and len(re.findall(r"u_and_u",tree))>0 and len(re.findall(r"'RULE', 'd_eq'",tree)) and len(re.findall(r'omega_and_omega', tree))==0 and len(re.findall(r'psi_implies_psi', tree))==0:
            curated_arr.append(res)
            curated = True"""

#-------------------------------------------------------------------------------------
print("starting 10")
# fg
for i in range(int(t_psi_fg_u/5)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_fg',tree))>0 and len(re.findall(r"u_and_u",tree))==0 and len(re.findall(r"u_implies_u",tree))==0 and len(re.findall(r"'RULE', 'gt'",tree)) and len(re.findall(r"omega_and_omega",tree))==0 and len(re.findall(r"psi_implies_psi",tree))==0:
            curated_arr.append(res)
            curated = True
for i in range(int(t_psi_fg_u/5)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_fg',tree))>0 and len(re.findall(r"u_and_u",tree))==0 and len(re.findall(r"u_implies_u",tree))==0 and len(re.findall(r"'RULE', 'lt'",tree)) and len(re.findall(r"omega_and_omega", tree))==0 and len(re.findall(r"psi_implies_psi", tree))==0:
            curated_arr.append(res)
            curated = True
for i in range(int(t_psi_fg_u/5)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_fg',tree))>0 and len(re.findall(r"u_and_u",tree))==0 and len(re.findall(r"u_implies_u",tree))==0 and len(re.findall(r"'RULE', 'eq'",tree)) and len(re.findall(r'omega_and_omega', tree))==0 and len(re.findall(r'psi_implies_psi', tree))==0:
            curated_arr.append(res)
            curated = True
"""for i in range(int(t_psi_fg_u/5)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_fg',tree))>0 and len(re.findall(r"u_and_u",tree))==0 and len(re.findall(r"u_implies_u",tree))==0 and len(re.findall(r"'RULE', 'd_gt'",tree)) and len(re.findall(r'omega_and_omega', tree))==0 and len(re.findall(r'psi_implies_psi', tree))==0:
            curated_arr.append(res)
            curated = True"""
for i in range(int(t_psi_fg_u/5)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_fg',tree))>0 and len(re.findall(r"u_and_u",tree))==0 and len(re.findall(r'u_implies_u',tree))==0 and len(re.findall(r"'RULE', 'd_lt'",tree)) and len(re.findall(r'omega_and_omega', tree))==0 and len(re.findall(r'psi_implies_psi', tree))==0:
            curated_arr.append(res)
            curated = True
for i in range(int(t_psi_fg_u/5)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_fg',tree))>0 and len(re.findall(r"u_and_u",tree))==0 and len(re.findall(r'u_implies_u',tree))==0 and len(re.findall(r"'RULE', 'd_eq'",tree)) and len(re.findall(r'omega_and_omega', tree))==0 and len(re.findall(r'psi_implies_psi', tree))==0:
            curated_arr.append(res)
            curated = True
# now f
print("starting 10")
for i in range(int(t_psi_f_u/5)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_f',tree))>0 and len(re.findall(r"u_and_u",tree))==0 and len(re.findall(r'u_implies_u',tree))==0 and len(re.findall(r"'RULE', 'gt'",tree)) and len(re.findall(r"omega_and_omega",tree))==0 and len(re.findall(r"psi_implies_psi",tree))==0:
            curated_arr.append(res)
            curated = True
for i in range(int(t_psi_f_u/5)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_f',tree))>0 and len(re.findall(r"u_and_u",tree))==0 and len(re.findall(r'u_implies_u',tree))==0 and len(re.findall(r"'RULE', 'lt'",tree)) and len(re.findall(r"omega_and_omega", tree))==0 and len(re.findall(r"psi_implies_psi", tree))==0:
            curated_arr.append(res)
            curated = True
for i in range(int(t_psi_f_u/5)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_f',tree))>0 and len(re.findall(r"u_and_u",tree))==0 and len(re.findall(r'u_implies_u',tree))==0 and len(re.findall(r"'RULE', 'eq'",tree)) and len(re.findall(r'omega_and_omega', tree))==0 and len(re.findall(r'psi_implies_psi', tree))==0:
            curated_arr.append(res)
            curated = True
for i in range(int(t_psi_f_u/5)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_f',tree))>0 and len(re.findall(r"u_and_u",tree))==0 and len(re.findall(r'u_implies_u',tree))==0 and len(re.findall(r"'RULE', 'd_gt'",tree)) and len(re.findall(r'omega_and_omega', tree))==0 and len(re.findall(r'psi_implies_psi', tree))==0:
            curated_arr.append(res)
            curated = True
"""for i in range(int(t_psi_f_u/5)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_f',tree))>0 and len(re.findall(r"u_and_u",tree))==0 and len(re.findall(r'u_implies_u',tree))==0 and len(re.findall(r"'RULE', 'd_lt'",tree)) and len(re.findall(r'omega_and_omega', tree))==0 and len(re.findall(r'psi_implies_psi', tree))==0:
            curated_arr.append(res)
            curated = True"""
for i in range(int(t_psi_f_u/5)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_f',tree))>0 and len(re.findall(r"u_and_u",tree))==0 and len(re.findall(r'u_implies_u',tree))==0 and len(re.findall(r"'RULE', 'd_eq'",tree)) and len(re.findall(r'omega_and_omega', tree))==0 and len(re.findall(r'psi_implies_psi', tree))==0:
            curated_arr.append(res)
            curated = True
print("starting 11")
# g
for i in range(int(t_psi_g_u/5)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_g',tree))>0 and len(re.findall(r"u_and_u",tree))==0 and len(re.findall(r'u_implies_u',tree))==0 and len(re.findall(r"'RULE', 'gt'",tree)) and len(re.findall(r"omega_and_omega",tree))==0 and len(re.findall(r"psi_implies_psi",tree))==0:
            curated_arr.append(res)
            curated = True
for i in range(int(t_psi_g_u/5)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_g',tree))>0 and len(re.findall(r"u_and_u",tree))==0 and len(re.findall(r'u_implies_u',tree))==0 and len(re.findall(r"'RULE', 'lt'",tree)) and len(re.findall(r"omega_and_omega", tree))==0 and len(re.findall(r"psi_implies_psi", tree))==0:
            curated_arr.append(res)
            curated = True
for i in range(int(t_psi_g_u/5)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_g',tree))>0 and len(re.findall(r"u_and_u",tree))==0 and len(re.findall(r'u_implies_u',tree))==0 and len(re.findall(r"'RULE', 'eq'",tree)) and len(re.findall(r'omega_and_omega', tree))==0 and len(re.findall(r'psi_implies_psi', tree))==0:
            curated_arr.append(res)
            curated = True
for i in range(int(t_psi_g_u/5)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_g',tree))>0 and len(re.findall(r"u_and_u",tree))==0 and len(re.findall(r'u_implies_u',tree))==0 and len(re.findall(r"'RULE', 'd_gt'",tree)) and len(re.findall(r'omega_and_omega', tree))==0 and len(re.findall(r'psi_implies_psi', tree))==0:
            curated_arr.append(res)
            curated = True
for i in range(int(t_psi_g_u/5)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_g',tree))>0 and len(re.findall(r"u_and_u",tree))==0 and len(re.findall(r'u_implies_u',tree))==0 and len(re.findall(r"'RULE', 'd_lt'",tree)) and len(re.findall(r'omega_and_omega', tree))==0 and len(re.findall(r'psi_implies_psi', tree))==0:
            curated_arr.append(res)
            curated = True
"""for i in range(int(t_psi_g_u/6)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_g',tree))>0 and len(re.findall(r"u_and_u",tree))==0 and len(re.findall(r'u_implies_u',tree))==0 and len(re.findall(r"'RULE', 'd_eq'",tree)) and len(re.findall(r'omega_and_omega', tree))==0 and len(re.findall(r'psi_implies_psi', tree))==0:
            curated_arr.append(res)
            curated = True"""
print("starting 12")

#------------------------------------------------------------------------------------- psi_implies_psi

# fg
for i in range(int(t_psi_implies_psi_fg_u_implies_u/5)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_fg',tree))>0 and len(re.findall(r"u_implies_u",tree))>0 and len(re.findall(r"'RULE', 'gt'",tree)) and len(re.findall(r"psi_implies_psi",tree))>0:
            curated_arr.append(res)
            curated = True
for i in range(int(t_psi_implies_psi_fg_u_implies_u/5)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_fg',tree))>0 and len(re.findall(r"u_implies_u",tree))>0 and len(re.findall(r"'RULE', 'lt'",tree)) and len(re.findall(r"psi_implies_psi", tree))>0:
            curated_arr.append(res)
            curated = True
for i in range(int(t_psi_implies_psi_fg_u_implies_u/5)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_fg',tree))>0 and len(re.findall(r"u_implies_u",tree))>0 and len(re.findall(r"'RULE', 'eq'",tree)) and len(re.findall(r'psi_implies_psi', tree))>0:
            curated_arr.append(res)
            curated = True
"""for i in range(int(t_psi_implies_psi_fg_u_implies_u/5)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_fg',tree))>0 and len(re.findall(r"u_implies_u",tree))>0 and len(re.findall(r"'RULE', 'd_gt'",tree)) and len(re.findall(r'psi_implies_psi', tree))>0:
            curated_arr.append(res)
            curated = True"""
for i in range(int(t_psi_implies_psi_fg_u_implies_u/5)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_fg',tree))>0 and len(re.findall(r"u_implies_u",tree))>0 and len(re.findall(r"'RULE', 'd_lt'",tree)) and len(re.findall(r'psi_implies_psi', tree))>0:
            curated_arr.append(res)
            curated = True
for i in range(int(t_psi_implies_psi_fg_u_implies_u/5)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_fg',tree))>0 and len(re.findall(r"u_implies_u",tree))>0 and len(re.findall(r"'RULE', 'd_eq'",tree)) and len(re.findall(r'psi_implies_psi', tree))>0:
            curated_arr.append(res)
            curated = True ################################################################################################################
# now f
print("starting 13")
for i in range(int(t_psi_implies_psi_f_u_implies_u/5)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_f',tree))>0 and len(re.findall(r"u_implies_u",tree))>0 and len(re.findall(r"'RULE', 'gt'",tree)) and len(re.findall(r"psi_implies_psi",tree))>0:
            curated_arr.append(res)
            curated = True
for i in range(int(t_psi_implies_psi_f_u_implies_u/5)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_f',tree))>0 and len(re.findall(r"u_implies_u",tree))>0 and len(re.findall(r"'RULE', 'lt'",tree)) and len(re.findall(r"psi_implies_psi", tree))>0:
            curated_arr.append(res)
            curated = True
for i in range(int(t_psi_implies_psi_f_u_implies_u/5)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_f',tree))>0 and len(re.findall(r"u_implies_u",tree))>0 and len(re.findall(r"'RULE', 'eq'",tree)) and len(re.findall(r'psi_implies_psi', tree))>0:
            curated_arr.append(res)
            curated = True
for i in range(int(t_psi_implies_psi_f_u_implies_u/5)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_f',tree))>0 and len(re.findall(r"u_implies_u",tree))>0 and len(re.findall(r"'RULE', 'd_gt'",tree)) and len(re.findall(r'psi_implies_psi', tree))>0:
            curated_arr.append(res)
            curated = True
"""for i in range(int(t_psi_implies_psi_f_u_implies_u/6)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_f',tree))>0 and len(re.findall(r"u_implies_u",tree))>0 and len(re.findall(r"'RULE', 'd_lt'",tree)) and len(re.findall(r'psi_implies_psi', tree))>0:
            curated_arr.append(res)
            curated = True"""
for i in range(int(t_psi_implies_psi_f_u_implies_u/5)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_f',tree))>0 and len(re.findall(r"u_implies_u",tree))>0 and len(re.findall(r"'RULE', 'd_eq'",tree)) and len(re.findall(r'psi_implies_psi', tree))>0:
            curated_arr.append(res)
            curated = True
print("starting 14")
# g
for i in range(int(t_psi_implies_psi_g_u_implies_u/5)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_g',tree))>0 and len(re.findall(r"u_implies_u",tree))>0 and len(re.findall(r"'RULE', 'gt'",tree)) and len(re.findall(r"psi_implies_psi",tree))>0:
            curated_arr.append(res)
            curated = True
for i in range(int(t_psi_implies_psi_g_u_implies_u/5)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_g',tree))>0 and len(re.findall(r"u_implies_u",tree))>0 and len(re.findall(r"'RULE', 'lt'",tree)) and len(re.findall(r"psi_implies_psi", tree))>0:
            curated_arr.append(res)
            curated = True
for i in range(int(t_psi_implies_psi_g_u_implies_u/5)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_g',tree))>0 and len(re.findall(r"u_implies_u",tree))>0 and len(re.findall(r"'RULE', 'eq'",tree)) and len(re.findall(r'psi_implies_psi', tree))>0:
            curated_arr.append(res)
            curated = True
for i in range(int(t_psi_implies_psi_g_u_implies_u/5)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_g',tree))>0 and len(re.findall(r"u_implies_u",tree))>0 and len(re.findall(r"'RULE', 'd_gt'",tree)) and len(re.findall(r'psi_implies_psi', tree))>0:
            curated_arr.append(res)
            curated = True
for i in range(int(t_psi_implies_psi_g_u_implies_u/5)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_g',tree))>0 and len(re.findall(r"u_implies_u",tree))>0 and len(re.findall(r"'RULE', 'd_lt'",tree)) and len(re.findall(r'psi_implies_psi', tree))>0:
            curated_arr.append(res)
            curated = True
"""for i in range(int(t_psi_implies_psi_g_u_implies_u/6)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_g',tree))>0 and len(re.findall(r"u_implies_u",tree))>0 and len(re.findall(r"'RULE', 'd_eq'",tree)) and len(re.findall(r'psi_implies_psi', tree))>0:
            curated_arr.append(res)
            curated = True"""
#-------------------------------------------------------------------------------------
print("s15")
# fg
for i in range(int(t_psi_implies_psi_fg_u_and_u/5)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_fg',tree))>0 and len(re.findall(r"u_and_u",tree))>0 and len(re.findall(r"'RULE', 'gt'",tree)) and len(re.findall(r"psi_implies_psi",tree))>0:
            curated_arr.append(res)
            curated = True
for i in range(int(t_psi_implies_psi_fg_u_and_u/5)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_fg',tree))>0 and len(re.findall(r"u_and_u",tree))>0 and len(re.findall(r"'RULE', 'lt'",tree)) and len(re.findall(r"psi_implies_psi", tree))>0:
            curated_arr.append(res)
            curated = True
for i in range(int(t_psi_implies_psi_fg_u_and_u/5)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_fg',tree))>0 and len(re.findall(r"u_and_u",tree))>0 and len(re.findall(r"'RULE', 'eq'",tree)) and len(re.findall(r'psi_implies_psi', tree))>0:
            curated_arr.append(res)
            curated = True
"""for i in range(int(t_psi_implies_psi_fg_u_and_u/6)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_fg',tree))>0 and len(re.findall(r"u_and_u",tree))>0 and len(re.findall(r"'RULE', 'd_gt'",tree)) and len(re.findall(r'psi_implies_psi', tree))>0:
            curated_arr.append(res)
            curated = True"""
for i in range(int(t_psi_implies_psi_fg_u_and_u/5)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_fg',tree))>0 and len(re.findall(r"u_and_u",tree))>0 and len(re.findall(r"'RULE', 'd_lt'",tree)) and len(re.findall(r'psi_implies_psi', tree))>0:
            curated_arr.append(res)
            curated = True
for i in range(int(t_psi_implies_psi_fg_u_and_u/5)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_fg',tree))>0 and len(re.findall(r"u_and_u",tree))>0 and len(re.findall(r"'RULE', 'd_eq'",tree)) and len(re.findall(r'psi_implies_psi', tree))>0:
            curated_arr.append(res) #####################################################################skdfjdlskfjsdlkfsjlkfjlsj3#########################
            curated = True
# now f
print("s16")
for i in range(int(t_psi_implies_psi_f_u_and_u/5)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_f',tree))>0 and len(re.findall(r"u_and_u",tree))>0 and len(re.findall(r"'RULE', 'gt'",tree)) and len(re.findall(r"psi_implies_psi",tree))>0:
            curated_arr.append(res)
            curated = True
for i in range(int(t_psi_implies_psi_f_u_and_u/5)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_f',tree))>0 and len(re.findall(r"u_and_u",tree))>0 and len(re.findall(r"'RULE', 'lt'",tree)) and len(re.findall(r"psi_implies_psi", tree))>0:
            curated_arr.append(res)
            curated = True
for i in range(int(t_psi_implies_psi_f_u_and_u/5)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_f',tree))>0 and len(re.findall(r"u_and_u",tree))>0 and len(re.findall(r"'RULE', 'eq'",tree)) and len(re.findall(r'psi_implies_psi', tree))>0:
            curated_arr.append(res)
            curated = True
for i in range(int(t_psi_implies_psi_f_u_and_u/5)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_f',tree))>0 and len(re.findall(r"u_and_u",tree))>0 and len(re.findall(r"'RULE', 'd_gt'",tree)) and len(re.findall(r'psi_implies_psi', tree))>0:
            curated_arr.append(res)
            curated = True
"""for i in range(int(t_psi_implies_psi_f_u_and_u/6)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_f',tree))>0 and len(re.findall(r"u_and_u",tree))>0 and len(re.findall(r"'RULE', 'd_lt'",tree)) and len(re.findall(r'psi_implies_psi', tree))>0:
            curated_arr.append(res)
            curated = True"""
for i in range(int(t_psi_implies_psi_f_u_and_u/5)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_f',tree))>0 and len(re.findall(r"u_and_u",tree))>0 and len(re.findall(r"'RULE', 'd_eq'",tree)) and len(re.findall(r'psi_implies_psi', tree))>0:
            curated_arr.append(res)
            curated = True
print("s17")
# g
for i in range(int(t_psi_implies_psi_g_u_and_u/5)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_g',tree))>0 and len(re.findall(r"u_and_u",tree))>0 and len(re.findall(r"'RULE', 'gt'",tree)) and len(re.findall(r"psi_implies_psi",tree))>0:
            curated_arr.append(res)
            curated = True
for i in range(int(t_psi_implies_psi_g_u_and_u/5)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_g',tree))>0 and len(re.findall(r"u_and_u",tree))>0 and len(re.findall(r"'RULE', 'lt'",tree)) and len(re.findall(r"psi_implies_psi", tree))>0:
            curated_arr.append(res)
            curated = True
for i in range(int(t_psi_implies_psi_g_u_and_u/5)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_g',tree))>0 and len(re.findall(r"u_and_u",tree))>0 and len(re.findall(r"'RULE', 'eq'",tree)) and len(re.findall(r'psi_implies_psi', tree))>0:
            curated_arr.append(res)
            curated = True
for i in range(int(t_psi_implies_psi_g_u_and_u/5)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_g',tree))>0 and len(re.findall(r"u_and_u",tree))>0 and len(re.findall(r"'RULE', 'd_gt'",tree)) and len(re.findall(r'psi_implies_psi', tree))>0:
            curated_arr.append(res)
            curated = True
for i in range(int(t_psi_implies_psi_g_u_and_u/5)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_g',tree))>0 and len(re.findall(r"u_and_u",tree))>0 and len(re.findall(r"'RULE', 'd_lt'",tree)) and len(re.findall(r'psi_implies_psi', tree))>0:
            curated_arr.append(res)
            curated = True
"""for i in range(int(t_psi_implies_psi_g_u_and_u/6)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_g',tree))>0 and len(re.findall(r"u_and_u",tree))>0 and len(re.findall(r"'RULE', 'd_eq'",tree)) and len(re.findall(r'psi_implies_psi', tree))>0:
            curated_arr.append(res)
            curated = True"""
print("s18")
#-------------------------------------------------------------------------------------

# fg
for i in range(int(t_psi_implies_psi_fg_u/5)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_fg',tree))>0 and len(re.findall(r"u_and_u",tree))==0 and len(re.findall(r"u_implies_u",tree))==0 and len(re.findall(r"'RULE', 'gt'",tree)) and len(re.findall(r"psi_implies_psi",tree))>0:
            curated_arr.append(res)
            curated = True
for i in range(int(t_psi_implies_psi_fg_u/5)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_fg',tree))>0 and len(re.findall(r"u_and_u",tree))==0 and len(re.findall(r"u_implies_u",tree))==0 and len(re.findall(r"'RULE', 'lt'",tree)) and len(re.findall(r"psi_implies_psi", tree))>0:
            curated_arr.append(res)
            curated = True
for i in range(int(t_psi_implies_psi_fg_u/5)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_fg',tree))>0 and len(re.findall(r"u_and_u",tree))==0 and len(re.findall(r"u_implies_u",tree))==0 and len(re.findall(r"'RULE', 'eq'",tree)) and len(re.findall(r'psi_implies_psi', tree))>0:
            curated_arr.append(res)
            curated = True
"""for i in range(int(t_psi_implies_psi_fg_u/6)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_fg',tree))>0 and len(re.findall(r"u_and_u",tree))==0 and len(re.findall(r"u_implies_u",tree))==0 and len(re.findall(r"'RULE', 'd_gt'",tree)) and len(re.findall(r'psi_implies_psi', tree))>0:
            curated_arr.append(res)
            curated = True"""
for i in range(int(t_psi_implies_psi_fg_u/5)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_fg',tree))>0 and len(re.findall(r"u_and_u",tree))==0 and len(re.findall(r'u_implies_u',tree))==0 and len(re.findall(r"'RULE', 'd_lt'",tree)) and len(re.findall(r'psi_implies_psi', tree))>0:
            curated_arr.append(res)
            curated = True
for i in range(int(t_psi_implies_psi_fg_u/5)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_fg',tree))>0 and len(re.findall(r"u_and_u",tree))==0 and len(re.findall(r'u_implies_u',tree))==0 and len(re.findall(r"'RULE', 'd_eq'",tree)) and len(re.findall(r'psi_implies_psi', tree))>0:
            curated_arr.append(res)
            curated = True
# now f
print("s19")
for i in range(int(t_psi_implies_psi_f_u/5)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_f',tree))>0 and len(re.findall(r"u_and_u",tree))==0 and len(re.findall(r'u_implies_u',tree))==0 and len(re.findall(r"'RULE', 'gt'",tree)) and len(re.findall(r"psi_implies_psi",tree))>0:
            curated_arr.append(res)
            curated = True
for i in range(int(t_psi_implies_psi_f_u/5)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_f',tree))>0 and len(re.findall(r"u_and_u",tree))==0 and len(re.findall(r'u_implies_u',tree))==0 and len(re.findall(r"'RULE', 'lt'",tree)) and len(re.findall(r"psi_implies_psi", tree))>0:
            curated_arr.append(res)
            curated = True
for i in range(int(t_psi_implies_psi_f_u/5)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_f',tree))>0 and len(re.findall(r"u_and_u",tree))==0 and len(re.findall(r'u_implies_u',tree))==0 and len(re.findall(r"'RULE', 'eq'",tree)) and len(re.findall(r'psi_implies_psi', tree))>0:
            curated_arr.append(res)
            curated = True
for i in range(int(t_psi_implies_psi_f_u/5)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_f',tree))>0 and len(re.findall(r"u_and_u",tree))==0 and len(re.findall(r'u_implies_u',tree))==0 and len(re.findall(r"'RULE', 'd_gt'",tree)) and len(re.findall(r'psi_implies_psi', tree))>0:
            curated_arr.append(res)
            curated = True
"""for i in range(int(t_psi_implies_psi_f_u/6)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_f',tree))>0 and len(re.findall(r"u_and_u",tree))==0 and len(re.findall(r'u_implies_u',tree))==0 and len(re.findall(r"'RULE', 'd_lt'",tree)) and len(re.findall(r'psi_implies_psi', tree))>0:
            curated_arr.append(res)
            curated = True"""
for i in range(int(t_psi_implies_psi_f_u/5)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_f',tree))>0 and len(re.findall(r"u_and_u",tree))==0 and len(re.findall(r'u_implies_u',tree))==0 and len(re.findall(r"'RULE', 'd_eq'",tree)) and len(re.findall(r'psi_implies_psi', tree))>0:
            curated_arr.append(res)
            curated = True
print("s20")
# g
for i in range(int(t_psi_implies_psi_g_u/5)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_g',tree))>0 and len(re.findall(r"u_and_u",tree))==0 and len(re.findall(r'u_implies_u',tree))==0 and len(re.findall(r"'RULE', 'gt'",tree)) and len(re.findall(r"psi_implies_psi",tree))>0:
            curated_arr.append(res)
            curated = True
for i in range(int(t_psi_implies_psi_g_u/5)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_g',tree))>0 and len(re.findall(r"u_and_u",tree))==0 and len(re.findall(r'u_implies_u',tree))==0 and len(re.findall(r"'RULE', 'lt'",tree)) and len(re.findall(r"psi_implies_psi", tree))>0:
            curated_arr.append(res)
            curated = True
for i in range(int(t_psi_implies_psi_g_u/5)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_g',tree))>0 and len(re.findall(r"u_and_u",tree))==0 and len(re.findall(r'u_implies_u',tree))==0 and len(re.findall(r"'RULE', 'eq'",tree)) and len(re.findall(r'psi_implies_psi', tree))>0:
            curated_arr.append(res)
            curated = True
for i in range(int(t_psi_implies_psi_g_u/5)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_g',tree))>0 and len(re.findall(r"u_and_u",tree))==0 and len(re.findall(r'u_implies_u',tree))==0 and len(re.findall(r"'RULE', 'd_gt'",tree)) and len(re.findall(r'psi_implies_psi', tree))>0:
            curated_arr.append(res)
            curated = True
for i in range(int(t_psi_implies_psi_g_u/5)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_g',tree))>0 and len(re.findall(r"u_and_u",tree))==0 and len(re.findall(r'u_implies_u',tree))==0 and len(re.findall(r"'RULE', 'd_lt'",tree)) and len(re.findall(r'psi_implies_psi', tree))>0:
            curated_arr.append(res)
            curated = True
"""for i in range(int(t_psi_implies_psi_g_u/6)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_g',tree))>0 and len(re.findall(r"u_and_u",tree))==0 and len(re.findall(r'u_implies_u',tree))==0 and len(re.findall(r"'RULE', 'd_eq'",tree)) and len(re.findall(r'psi_implies_psi', tree))>0:
            curated_arr.append(res)
            curated = True"""
print("s22")                                                                                                                                                                      
# fg
for i in range(int(t_omega_and_omega_fg_u_implies_u/5)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_fg',tree))>0 and len(re.findall(r"u_implies_u",tree))>0 and len(re.findall(r"'RULE', 'gt'",tree)) and len(re.findall(r"omega_and_omega",tree))>0:
            curated_arr.append(res)
            curated = True
for i in range(int(t_omega_and_omega_fg_u_implies_u/5)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_fg',tree))>0 and len(re.findall(r"u_implies_u",tree))>0 and len(re.findall(r"'RULE', 'lt'",tree)) and len(re.findall(r"omega_and_omega", tree))>0:
            curated_arr.append(res)
            curated = True
for i in range(int(t_omega_and_omega_fg_u_implies_u/5)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_fg',tree))>0 and len(re.findall(r"u_implies_u",tree))>0 and len(re.findall(r"'RULE', 'eq'",tree)) and len(re.findall(r'omega_and_omega', tree))>0:
            curated_arr.append(res)
            curated = True
"""for i in range(int(t_omega_and_omega_fg_u_implies_u/6)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_fg',tree))>0 and len(re.findall(r"u_implies_u",tree))>0 and len(re.findall(r"'RULE', 'd_gt'",tree)) and len(re.findall(r'omega_and_omega', tree))>0:
            curated_arr.append(res)
            curated = True"""
for i in range(int(t_omega_and_omega_fg_u_implies_u/5)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_fg',tree))>0 and len(re.findall(r"u_implies_u",tree))>0 and len(re.findall(r"'RULE', 'd_lt'",tree)) and len(re.findall(r'omega_and_omega', tree))>0:
            curated_arr.append(res)
            curated = True
for i in range(int(t_omega_and_omega_fg_u_implies_u/5)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_fg',tree))>0 and len(re.findall(r"u_implies_u",tree))>0 and len(re.findall(r"'RULE', 'd_eq'",tree)) and len(re.findall(r'omega_and_omega', tree))>0:
            curated_arr.append(res)
            curated = True ################################################################################################################
# now f

for i in range(int(t_omega_and_omega_f_u_implies_u/5)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_f',tree))>0 and len(re.findall(r"u_implies_u",tree))>0 and len(re.findall(r"'RULE', 'gt'",tree)) and len(re.findall(r"omega_and_omega",tree))>0:
            curated_arr.append(res)
            curated = True
for i in range(int(t_omega_and_omega_f_u_implies_u/5)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_f',tree))>0 and len(re.findall(r"u_implies_u",tree))>0 and len(re.findall(r"'RULE', 'lt'",tree)) and len(re.findall(r"omega_and_omega", tree))>0:
            curated_arr.append(res)
            curated = True
for i in range(int(t_omega_and_omega_f_u_implies_u/5)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_f',tree))>0 and len(re.findall(r"u_implies_u",tree))>0 and len(re.findall(r"'RULE', 'eq'",tree)) and len(re.findall(r'omega_and_omega', tree))>0:
            curated_arr.append(res)
            curated = True
for i in range(int(t_omega_and_omega_f_u_implies_u/5)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_f',tree))>0 and len(re.findall(r"u_implies_u",tree))>0 and len(re.findall(r"'RULE', 'd_gt'",tree)) and len(re.findall(r'omega_and_omega', tree))>0:
            curated_arr.append(res)
            curated = True
"""for i in range(int(t_omega_and_omega_f_u_implies_u/6)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_f',tree))>0 and len(re.findall(r"u_implies_u",tree))>0 and len(re.findall(r"'RULE', 'd_lt'",tree)) and len(re.findall(r'omega_and_omega', tree))>0:
            curated_arr.append(res)
            curated = True"""
for i in range(int(t_omega_and_omega_f_u_implies_u/5)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_f',tree))>0 and len(re.findall(r"u_implies_u",tree))>0 and len(re.findall(r"'RULE', 'd_eq'",tree)) and len(re.findall(r'omega_and_omega', tree))>0:
            curated_arr.append(res)
            curated = True
print("s23")
# g
for i in range(int(t_omega_and_omega_g_u_implies_u/5)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_g',tree))>0 and len(re.findall(r"u_implies_u",tree))>0 and len(re.findall(r"'RULE', 'gt'",tree)) and len(re.findall(r"omega_and_omega",tree))>0:
            curated_arr.append(res)
            curated = True
for i in range(int(t_omega_and_omega_g_u_implies_u/5)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_g',tree))>0 and len(re.findall(r"u_implies_u",tree))>0 and len(re.findall(r"'RULE', 'lt'",tree)) and len(re.findall(r"omega_and_omega", tree))>0:
            curated_arr.append(res)
            curated = True
for i in range(int(t_omega_and_omega_g_u_implies_u/5)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_g',tree))>0 and len(re.findall(r"u_implies_u",tree))>0 and len(re.findall(r"'RULE', 'eq'",tree)) and len(re.findall(r'omega_and_omega', tree))>0:
            curated_arr.append(res)
            curated = True
for i in range(int(t_omega_and_omega_g_u_implies_u/5)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_g',tree))>0 and len(re.findall(r"u_implies_u",tree))>0 and len(re.findall(r"'RULE', 'd_gt'",tree)) and len(re.findall(r'omega_and_omega', tree))>0:
            curated_arr.append(res)
            curated = True
for i in range(int(t_omega_and_omega_g_u_implies_u/5)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_g',tree))>0 and len(re.findall(r"u_implies_u",tree))>0 and len(re.findall(r"'RULE', 'd_lt'",tree)) and len(re.findall(r'omega_and_omega', tree))>0:
            curated_arr.append(res)
            curated = True
"""for i in range(int(t_omega_and_omega_g_u_implies_u/6)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_g',tree))>0 and len(re.findall(r"u_implies_u",tree))>0 and len(re.findall(r"'RULE', 'd_eq'",tree)) and len(re.findall(r'omega_and_omega', tree))>0:
            curated_arr.append(res)
            curated = True"""
#-------------------------------------------------------------------------------------
print("s24")
# fg
for i in range(int(t_omega_and_omega_fg_u_and_u/5)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_fg',tree))>0 and len(re.findall(r"u_and_u",tree))>0 and len(re.findall(r"'RULE', 'gt'",tree)) and len(re.findall(r"omega_and_omega",tree))>0:
            curated_arr.append(res)
            curated = True
for i in range(int(t_omega_and_omega_fg_u_and_u/5)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_fg',tree))>0 and len(re.findall(r"u_and_u",tree))>0 and len(re.findall(r"'RULE', 'lt'",tree)) and len(re.findall(r"omega_and_omega", tree))>0:
            curated_arr.append(res)
            curated = True
for i in range(int(t_omega_and_omega_fg_u_and_u/5)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_fg',tree))>0 and len(re.findall(r"u_and_u",tree))>0 and len(re.findall(r"'RULE', 'eq'",tree)) and len(re.findall(r'omega_and_omega', tree))>0:
            curated_arr.append(res)
            curated = True
"""for i in range(int(t_omega_and_omega_fg_u_and_u/6)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_fg',tree))>0 and len(re.findall(r"u_and_u",tree))>0 and len(re.findall(r"'RULE', 'd_gt'",tree)) and len(re.findall(r'omega_and_omega', tree))>0:
            curated_arr.append(res)
            curated = True"""
for i in range(int(t_omega_and_omega_fg_u_and_u/5)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_fg',tree))>0 and len(re.findall(r"u_and_u",tree))>0 and len(re.findall(r"'RULE', 'd_lt'",tree)) and len(re.findall(r'omega_and_omega', tree))>0:
            curated_arr.append(res)
            curated = True
for i in range(int(t_omega_and_omega_fg_u_and_u/5)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_fg',tree))>0 and len(re.findall(r"u_and_u",tree))>0 and len(re.findall(r"'RULE', 'd_eq'",tree)) and len(re.findall(r'omega_and_omega', tree))>0:
            curated_arr.append(res)
            curated = True
# now f
print("s26")
for i in range(int(t_omega_and_omega_f_u_and_u/5)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_f',tree))>0 and len(re.findall(r"u_and_u",tree))>0 and len(re.findall(r"'RULE', 'gt'",tree)) and len(re.findall(r"omega_and_omega",tree))>0:
            curated_arr.append(res)
            curated = True
for i in range(int(t_omega_and_omega_f_u_and_u/5)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_f',tree))>0 and len(re.findall(r"u_and_u",tree))>0 and len(re.findall(r"'RULE', 'lt'",tree)) and len(re.findall(r"omega_and_omega", tree))>0:
            curated_arr.append(res)
            curated = True
for i in range(int(t_omega_and_omega_f_u_and_u/5)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_f',tree))>0 and len(re.findall(r"u_and_u",tree))>0 and len(re.findall(r"'RULE', 'eq'",tree)) and len(re.findall(r'omega_and_omega', tree))>0:
            curated_arr.append(res)
            curated = True
for i in range(int(t_omega_and_omega_f_u_and_u/5)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_f',tree))>0 and len(re.findall(r"u_and_u",tree))>0 and len(re.findall(r"'RULE', 'd_gt'",tree)) and len(re.findall(r'omega_and_omega', tree))>0:
            curated_arr.append(res)
            curated = True
"""for i in range(int(t_omega_and_omega_f_u_and_u/6)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_f',tree))>0 and len(re.findall(r"u_and_u",tree))>0 and len(re.findall(r"'RULE', 'd_lt'",tree)) and len(re.findall(r'omega_and_omega', tree))>0:
            curated_arr.append(res)
            curated = True"""
for i in range(int(t_omega_and_omega_f_u_and_u/5)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_f',tree))>0 and len(re.findall(r"u_and_u",tree))>0 and len(re.findall(r"'RULE', 'd_eq'",tree)) and len(re.findall(r'omega_and_omega', tree))>0:
            curated_arr.append(res)
            curated = True
print("s27")
# g
for i in range(int(t_omega_and_omega_g_u_and_u/5)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_g',tree))>0 and len(re.findall(r"u_and_u",tree))>0 and len(re.findall(r"'RULE', 'gt'",tree)) and len(re.findall(r"omega_and_omega",tree))>0:
            curated_arr.append(res)
            curated = True
for i in range(int(t_omega_and_omega_g_u_and_u/5)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_g',tree))>0 and len(re.findall(r"u_and_u",tree))>0 and len(re.findall(r"'RULE', 'lt'",tree)) and len(re.findall(r"omega_and_omega", tree))>0:
            curated_arr.append(res)
            curated = True
for i in range(int(t_omega_and_omega_g_u_and_u/5)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_g',tree))>0 and len(re.findall(r"u_and_u",tree))>0 and len(re.findall(r"'RULE', 'eq'",tree)) and len(re.findall(r'omega_and_omega', tree))>0:
            curated_arr.append(res)
            curated = True
for i in range(int(t_omega_and_omega_g_u_and_u/5)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_g',tree))>0 and len(re.findall(r"u_and_u",tree))>0 and len(re.findall(r"'RULE', 'd_gt'",tree)) and len(re.findall(r'omega_and_omega', tree))>0:
            curated_arr.append(res)
            curated = True
for i in range(int(t_omega_and_omega_g_u_and_u/5)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_g',tree))>0 and len(re.findall(r"u_and_u",tree))>0 and len(re.findall(r"'RULE', 'd_lt'",tree)) and len(re.findall(r'omega_and_omega', tree))>0:
            curated_arr.append(res)
            curated = True
"""for i in range(int(t_omega_and_omega_g_u_and_u/6)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_g',tree))>0 and len(re.findall(r"u_and_u",tree))>0 and len(re.findall(r"'RULE', 'd_eq'",tree)) and len(re.findall(r'omega_and_omega', tree))>0:
            curated_arr.append(res)
            curated = True
"""
#-------------------------------------------------------------------------------------
print("s28")
# fg
for i in range(int(t_omega_and_omega_fg_u/5)): ######################################################################ooooooooooooooooooooooooooooooooooooooooooo
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_fg',tree))>0 and len(re.findall(r"u_and_u",tree))==0 and len(re.findall(r"u_implies_u",tree))==0 and len(re.findall(r"'RULE', 'gt'",tree)) and len(re.findall(r"omega_and_omega",tree))>0:
            curated_arr.append(res)
            curated = True
for i in range(int(t_omega_and_omega_fg_u/5)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_fg',tree))>0 and len(re.findall(r"u_and_u",tree))==0 and len(re.findall(r"u_implies_u",tree))==0 and len(re.findall(r"'RULE', 'lt'",tree)) and len(re.findall(r"omega_and_omega", tree))>0:
            curated_arr.append(res)
            curated = True
for i in range(int(t_omega_and_omega_fg_u/5)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_fg',tree))>0 and len(re.findall(r"u_and_u",tree))==0 and len(re.findall(r"u_implies_u",tree))==0 and len(re.findall(r"'RULE', 'eq'",tree)) and len(re.findall(r'omega_and_omega', tree))>0:
            curated_arr.append(res)
            curated = True
"""for i in range(int(t_omega_and_omega_fg_u/6)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_fg',tree))>0 and len(re.findall(r"u_and_u",tree))==0 and len(re.findall(r"u_implies_u",tree))==0 and len(re.findall(r"'RULE', 'd_gt'",tree)) and len(re.findall(r'omega_and_omega', tree))>0:
            curated_arr.append(res)
            curated = True"""
for i in range(int(t_omega_and_omega_fg_u/5)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_fg',tree))>0 and len(re.findall(r"u_and_u",tree))==0 and len(re.findall(r'u_implies_u',tree))==0 and len(re.findall(r"'RULE', 'd_lt'",tree)) and len(re.findall(r'omega_and_omega', tree))>0:
            curated_arr.append(res)
            curated = True
for i in range(int(t_omega_and_omega_fg_u/5)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_fg',tree))>0 and len(re.findall(r"u_and_u",tree))==0 and len(re.findall(r'u_implies_u',tree))==0 and len(re.findall(r"'RULE', 'd_eq'",tree)) and len(re.findall(r'omega_and_omega', tree))>0:
            curated_arr.append(res)
            curated = True
# now f
print("s29")
for i in range(int(t_omega_and_omega_f_u/5)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_f',tree))>0 and len(re.findall(r"u_and_u",tree))==0 and len(re.findall(r'u_implies_u',tree))==0 and len(re.findall(r"'RULE', 'gt'",tree)) and len(re.findall(r"omega_and_omega",tree))>0:
            curated_arr.append(res)
            curated = True
for i in range(int(t_omega_and_omega_f_u/5)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_f',tree))>0 and len(re.findall(r"u_and_u",tree))==0 and len(re.findall(r'u_implies_u',tree))==0 and len(re.findall(r"'RULE', 'lt'",tree)) and len(re.findall(r"omega_and_omega", tree))>0:
            curated_arr.append(res)
            curated = True
for i in range(int(t_omega_and_omega_f_u/5)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_f',tree))>0 and len(re.findall(r"u_and_u",tree))==0 and len(re.findall(r'u_implies_u',tree))==0 and len(re.findall(r"'RULE', 'eq'",tree)) and len(re.findall(r'omega_and_omega', tree))>0:
            curated_arr.append(res)
            curated = True
for i in range(int(t_omega_and_omega_f_u/5)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_f',tree))>0 and len(re.findall(r"u_and_u",tree))==0 and len(re.findall(r'u_implies_u',tree))==0 and len(re.findall(r"'RULE', 'd_gt'",tree)) and len(re.findall(r'omega_and_omega', tree))>0:
            curated_arr.append(res)
            curated = True
"""for i in range(int(t_omega_and_omega_f_u/6)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_f',tree))>0 and len(re.findall(r"u_and_u",tree))==0 and len(re.findall(r'u_implies_u',tree))==0 and len(re.findall(r"'RULE', 'd_lt'",tree)) and len(re.findall(r'omega_and_omega', tree))>0:
            curated_arr.append(res)
            curated = True"""
for i in range(int(t_omega_and_omega_f_u/5)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_f',tree))>0 and len(re.findall(r"u_and_u",tree))==0 and len(re.findall(r'u_implies_u',tree))==0 and len(re.findall(r"'RULE', 'd_eq'",tree)) and len(re.findall(r'omega_and_omega', tree))>0:
            curated_arr.append(res)
            curated = True
print("s30")
# g
for i in range(int(t_omega_and_omega_g_u/5)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_g',tree))>0 and len(re.findall(r"u_and_u",tree))==0 and len(re.findall(r'u_implies_u',tree))==0 and len(re.findall(r"'RULE', 'gt'",tree)) and len(re.findall(r"omega_and_omega",tree))>0:
            curated_arr.append(res)
            curated = True
for i in range(int(t_omega_and_omega_g_u/5)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_g',tree))>0 and len(re.findall(r"u_and_u",tree))==0 and len(re.findall(r'u_implies_u',tree))==0 and len(re.findall(r"'RULE', 'lt'",tree)) and len(re.findall(r"omega_and_omega", tree))>0:
            curated_arr.append(res)
            curated = True
for i in range(int(t_omega_and_omega_g_u/5)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_g',tree))>0 and len(re.findall(r"u_and_u",tree))==0 and len(re.findall(r'u_implies_u',tree))==0 and len(re.findall(r"'RULE', 'eq'",tree)) and len(re.findall(r'omega_and_omega', tree))>0:
            curated_arr.append(res)
            curated = True
for i in range(int(t_omega_and_omega_g_u/5)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_g',tree))>0 and len(re.findall(r"u_and_u",tree))==0 and len(re.findall(r'u_implies_u',tree))==0 and len(re.findall(r"'RULE', 'd_gt'",tree)) and len(re.findall(r'omega_and_omega', tree))>0:
            curated_arr.append(res)
            curated = True
for i in range(int(t_omega_and_omega_g_u/5)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_g',tree))>0 and len(re.findall(r"u_and_u",tree))==0 and len(re.findall(r'u_implies_u',tree))==0 and len(re.findall(r"'RULE', 'd_lt'",tree)) and len(re.findall(r'omega_and_omega', tree))>0:
            curated_arr.append(res)
            curated = True
"""for i in range(int(t_omega_and_omega_g_u/6)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_g',tree))>0 and len(re.findall(r"u_and_u",tree))==0 and len(re.findall(r'u_implies_u',tree))==0 and len(re.findall(r"'RULE', 'd_eq'",tree)) and len(re.findall(r'omega_and_omega', tree))>0:
            curated_arr.append(res)
            curated = True"""
print("done gen")
print(f'curated: {len(curated_arr)}')
try:
    with open(f'../pkl/curated_dataset.pkl', 'wb') as results:
        pickle.dump(curated_arr, results)
except Exception as e:
    print(e)

#--------------------------------------------------------------------------------------
"""
        fg_found = True if len(re.findall(r'temp_op_fg',tree)) > 0 else False
        f_found = True if len(re.findall(r'temp_op_f',tree)) > 0 else False
        g_found = True if len(re.findall(r'temp_op_g',tree)) > 0 else False

        c_hi_found = True if len(re.findall(r'C_HIGH', tree)) > 0 else False
        c_mid_found = True if len(re.findall(r'C_MID', tree)) > 0 else False
        c_lo_found = True if len(re.findall(r'C_LOW', tree)) > 0 else False

        implies_found = True if len(re.findall(r'implies', sample)) > 0 else False
        and_found = True if len(re.findall(r'and', sample)) > 0 else False

        # for s in signals:
        gt_found = True if len(re.findall(r"'RULE', 'gt'",tree)) > 0 else False
        lt_found = True if len(re.findall(r"'RULE', 'lt'",tree)) > 0 else False
        eq_found = True if len(re.findall(r"'RULE', 'eq'",tree)) > 0 else False
        d_gt_found = True if len(re.findall(r"'RULE', 'd_gt'",tree)) > 0 else False
        d_lt_found = True if len(re.findall(r"'RULE', 'd_lt'",tree)) > 0 else False
        d_eq_found = True if len(re.findall(r"'RULE', 'd_eq'",tree)) > 0 else False
"""

# Evaluate final statistics of the dataset - do this later

