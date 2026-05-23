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

file_name = f'./config/config_nx_3_ny_1_nz_18_final_test_set.json'
    
with open(file_name, 'r', encoding='utf-8') as f:
    params = json.load(f)

ids = params["ids"]

for x in ids:
    print(repr(x), [hex(ord(c)) for c in x])

grammar = params['grammar']
parser = Lark(grammar)
stl_base_instance = STLBase(params['grammar'], params["ids"])

def check_time_intervals(sample):
    # also check for ranges time interval
    time_interval_num_num = r'\[\d+,\d+\]'
    time_interval_inf_num = r'\[inf,\d+\]'
    time_interval_inf_inf = r'\[inf,inf\]'

    if len(re.findall(time_interval_inf_inf, sample)) > 0 or len(re.findall(time_interval_inf_num, sample)) > 0:
        return False
    
    intervals = re.findall(time_interval_num_num, sample)    
    if intervals is not None:
        for interval in intervals:
            t_a = interval.split(',')[0][1:]
            t_b = interval.split(',')[1][:-1]
            if int(t_b) <= int(t_a):
                return False
    return True

# Large 5K dataset
large_dataset = []

# Obtain 5K samples
for i in range(20000):
    a = stl_base_instance.sample('omega')
    while len(a) > 90 or check_time_intervals(a) is False:
        a = stl_base_instance.sample('omega')
    large_dataset.append(a)

# From the 5K samples, create curated dataset with desired percentages

curated_size = 300 
curated_arr = []
curated = False

# First determine the size of each bucket
non_temporal_samples = int(math.floor(0.3 * curated_size))

non_temporal_u = math.floor(0.2 * non_temporal_samples)
non_temporal_u_and_u = int(math.floor(0.3 * non_temporal_samples))
non_temporal_u_implies_u = non_temporal_samples - non_temporal_u - non_temporal_u_and_u

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

t_omega_and_omega_fg_u_implies_u = int(math.floor(0.25 * t_omega_and_omega_fg))
t_omega_and_omega_fg_u_and_u = int(math.floor(0.25 * t_omega_and_omega_fg))
t_omega_and_omega_fg_u = t_omega_and_omega_fg - t_omega_and_omega_fg_u_implies_u - t_omega_and_omega_fg_u_and_u

t_omega_and_omega_f_u_implies_u = int(math.floor(0.25 * t_omega_and_omega_f))
t_omega_and_omega_f_u_and_u = int(math.floor(0.25 * t_omega_and_omega_f))
t_omega_and_omega_f_u = t_omega_and_omega_f - t_omega_and_omega_f_u_implies_u - t_omega_and_omega_f_u_and_u

t_omega_and_omega_g_u_implies_u = int(math.floor(0.25 * t_omega_and_omega_g))
t_omega_and_omega_g_u_and_u = int(math.floor(0.25 * t_omega_and_omega_g))
t_omega_and_omega_g_u = t_omega_and_omega_g - t_omega_and_omega_g_u_implies_u - t_omega_and_omega_g_u_and_u

t_psi_fg_u_implies_u = int(math.floor(0.25 * t_psi_fg))
t_psi_fg_u_and_u = int(math.floor(0.25 * t_psi_fg))
t_psi_fg_u = t_psi_fg - t_psi_fg_u_implies_u - t_psi_fg_u_and_u

t_psi_f_u_implies_u = int(math.floor(0.25 * t_psi_f))
t_psi_f_u_and_u = int(math.floor(0.25 * t_psi_f))
t_psi_f_u = t_psi_f - t_psi_f_u_implies_u - t_psi_f_u_and_u

t_psi_g_u_implies_u = int(math.floor(0.25 * t_psi_g))
t_psi_g_u_and_u = int(math.floor(0.25 * t_psi_g))
t_psi_g_u = t_psi_g - t_psi_g_u_implies_u - t_psi_g_u_and_u

# Each of those 9 categories for the 4 types needs to be split into 6 ways for each of the operators
# Then sample to fill each bucket, checking that the samples fulfill the bucket requirements before adding them
curated = False
for i in range(non_temporal_u_gt):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if (len(re.findall(r'temp_op_fg',tree))==0 and len(re.findall(r'temp_op_f',tree))==0 and len(re.findall(r'temp_op_g',tree))==0) and len(re.findall(r"'RULE', 'gt'",tree))>0:
            curated_arr.append(res)
            curated = True

for i in range(non_temporal_u_lt):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if (len(re.findall(r'temp_op_fg',tree))==0 and len(re.findall(r'temp_op_f',tree))==0 and len(re.findall(r'temp_op_g',tree))==0) and len(re.findall(r"'RULE', 'lt'",tree))>0:
            curated_arr.append(res)
            curated = True

for i in range(non_temporal_u_eq):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if (len(re.findall(r'temp_op_fg',tree))==0 and len(re.findall(r'temp_op_f',tree))==0 and len(re.findall(r'temp_op_g',tree))==0) and len(re.findall(r"'RULE', 'eq'",tree))>0:
            curated_arr.append(res)
            curated = True

for i in range(non_temporal_u_d_lt):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if (len(re.findall(r'temp_op_fg',tree))==0 and len(re.findall(r'temp_op_f',tree))==0 and len(re.findall(r'temp_op_g',tree))==0) and len(re.findall(r"'RULE', 'd_lt'",tree))>0:
            curated_arr.append(res)
            curated = True

for i in range(non_temporal_u_d_eq):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if (len(re.findall(r'temp_op_fg',tree))==0 and len(re.findall(r'temp_op_f',tree))==0 and len(re.findall(r'temp_op_g',tree))==0) and len(re.findall(r"'RULE', 'd_eq'",tree))>0:
            curated_arr.append(res)
            curated = True

for i in range(non_temporal_u_and_u_gt):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if (len(re.findall(r'temp_op_fg',tree))==0 and len(re.findall(r'temp_op_f',tree))==0 and len(re.findall(r'temp_op_g',tree))==0) and len(re.findall(r"'RULE', 'gt'",tree))>0 and len(re.findall(r"u_and_u",tree))>0:
            curated_arr.append(res)
            curated = True

for i in range(non_temporal_u_and_u_lt):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if (len(re.findall(r'temp_op_fg',tree))==0 and len(re.findall(r'temp_op_f',tree))==0 and len(re.findall(r'temp_op_g',tree))==0) and len(re.findall(r"'RULE', 'lt'",tree))>0 and len(re.findall(r"u_and_u",tree))>0:
            curated_arr.append(res)
            curated = True

for i in range(non_temporal_u_and_u_eq):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if (len(re.findall(r'temp_op_fg',tree))==0 and len(re.findall(r'temp_op_f',tree))==0 and len(re.findall(r'temp_op_g',tree))==0) and len(re.findall(r"'RULE', 'eq'",tree))>0 and len(re.findall(r"u_and_u",tree))>0:
            curated_arr.append(res)
            curated = True

for i in range(non_temporal_u_and_u_d_gt):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if (len(re.findall(r'temp_op_fg',tree))==0 and len(re.findall(r'temp_op_f',tree))==0 and len(re.findall(r'temp_op_g',tree))==0) and len(re.findall(r"'RULE', 'd_gt'",tree))>0 and len(re.findall(r"u_and_u",tree))>0:
            curated_arr.append(res)
            curated = True

for i in range(non_temporal_u_and_u_d_eq):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if (len(re.findall(r'temp_op_fg',tree))==0 and len(re.findall(r'temp_op_f',tree))==0 and len(re.findall(r'temp_op_g',tree))==0) and len(re.findall(r"'RULE', 'd_eq'",tree))>0 and len(re.findall(r"u_and_u",tree))>0:
            curated_arr.append(res)
            curated = True

for i in range(non_temporal_u_implies_u_gt):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if (len(re.findall(r'temp_op_fg',tree))==0 and len(re.findall(r'temp_op_f',tree))==0 and len(re.findall(r'temp_op_g',tree))==0) and len(re.findall(r"'RULE', 'gt'",tree))>0 and len(re.findall(r"u_implies_u",tree))>0:
            curated_arr.append(res)
            curated = True

for i in range(non_temporal_u_implies_u_lt):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if (len(re.findall(r'temp_op_fg',tree))==0 and len(re.findall(r'temp_op_f',tree))==0 and len(re.findall(r'temp_op_g',tree))==0) and len(re.findall(r"'RULE', 'lt'",tree))>0 and len(re.findall(r"u_implies_u",tree))>0:
            curated_arr.append(res)
            curated = True

for i in range(non_temporal_u_implies_u_eq):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if (len(re.findall(r'temp_op_fg',tree))==0 and len(re.findall(r'temp_op_f',tree))==0 and len(re.findall(r'temp_op_g',tree))==0) and len(re.findall(r"'RULE', 'eq'",tree))>0 and len(re.findall(r"u_implies_u",tree))>0:
            curated_arr.append(res)
            curated = True

for i in range(non_temporal_u_implies_u_d_gt):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if (len(re.findall(r'temp_op_fg',tree))==0 and len(re.findall(r'temp_op_f',tree))==0 and len(re.findall(r'temp_op_g',tree))==0) and len(re.findall(r"'RULE', 'd_gt'",tree))>0 and len(re.findall(r"u_implies_u",tree))>0:
            curated_arr.append(res)
            curated = True

for i in range(non_temporal_u_implies_u_d_lt):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if (len(re.findall(r'temp_op_fg',tree))==0 and len(re.findall(r'temp_op_f',tree))==0 and len(re.findall(r'temp_op_g',tree))==0) and len(re.findall(r"'RULE', 'd_lt'",tree))>0 and len(re.findall(r"u_implies_u",tree))>0:
            curated_arr.append(res)
            curated = True

for i in range(int(t_psi_fg_u_implies_u/5)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_fg',tree))>0 and len(re.findall(r"'RULE', 'gt'",tree)) and len(re.findall(r"omega_and_omega",tree))==0 and len(re.findall(r"psi_implies_psi",tree))==0:
            curated_arr.append(res)
            curated = True
            
for i in range(int(t_psi_fg_u_implies_u/5)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_fg',tree))>0 and len(re.findall(r"'RULE', 'lt'",tree)) and len(re.findall(r"omega_and_omega", tree))==0 and len(re.findall(r"psi_implies_psi", tree))==0:
            curated_arr.append(res)
            curated = True
            
for i in range(int(t_psi_fg_u_implies_u/5)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_fg',tree))>0 and len(re.findall(r"'RULE', 'eq'",tree)) and len(re.findall(r'omega_and_omega', tree))==0 and len(re.findall(r'psi_implies_psi', tree))==0:
            curated_arr.append(res)
            curated = True
            
for i in range(int(t_psi_fg_u_implies_u/5)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_fg',tree))>0 and len(re.findall(r"'RULE', 'd_lt'",tree)) and len(re.findall(r'omega_and_omega', tree))==0 and len(re.findall(r'psi_implies_psi', tree))==0:
            curated_arr.append(res)
            curated = True
            
for i in range(int(t_psi_fg_u_implies_u/5)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_fg',tree))>0 and len(re.findall(r"'RULE', 'd_eq'",tree)) and len(re.findall(r'omega_and_omega', tree))==0 and len(re.findall(r'psi_implies_psi', tree))==0:
            curated_arr.append(res)
            curated = True

for i in range(int(t_psi_f_u_implies_u/5)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_f',tree))>0 and len(re.findall(r"'RULE', 'gt'",tree)) and len(re.findall(r"omega_and_omega",tree))==0 and len(re.findall(r"psi_implies_psi",tree))==0:
            curated_arr.append(res)
            curated = True
            
for i in range(int(t_psi_f_u_implies_u/5)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_f',tree))>0 and len(re.findall(r"'RULE', 'lt'",tree)) and len(re.findall(r"omega_and_omega", tree))==0 and len(re.findall(r"psi_implies_psi", tree))==0:
            curated_arr.append(res)
            curated = True
            
for i in range(int(t_psi_f_u_implies_u/5)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_f',tree))>0 and len(re.findall(r"'RULE', 'eq'",tree)) and len(re.findall(r'omega_and_omega', tree))==0 and len(re.findall(r'psi_implies_psi', tree))==0:
            curated_arr.append(res)
            curated = True
            
for i in range(int(t_psi_f_u_implies_u/5)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_f',tree))>0 and len(re.findall(r"'RULE', 'd_gt'",tree)) and len(re.findall(r'omega_and_omega', tree))==0 and len(re.findall(r'psi_implies_psi', tree))==0:
            curated_arr.append(res)
            curated = True
            
for i in range(int(t_psi_f_u_implies_u/5)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_f',tree))>0 and len(re.findall(r"'RULE', 'd_eq'",tree)) and len(re.findall(r'omega_and_omega', tree))==0 and len(re.findall(r'psi_implies_psi', tree))==0:
            curated_arr.append(res)
            curated = True

for i in range(int(t_psi_g_u_implies_u/5)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_g',tree))>0 and len(re.findall(r"'RULE', 'gt'",tree)) and len(re.findall(r"omega_and_omega",tree))==0 and len(re.findall(r"psi_implies_psi",tree))==0:
            curated_arr.append(res)
            curated = True
            
for i in range(int(t_psi_g_u_implies_u/5)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_g',tree))>0 and len(re.findall(r"'RULE', 'lt'",tree)) and len(re.findall(r"omega_and_omega", tree))==0 and len(re.findall(r"psi_implies_psi", tree))==0:
            curated_arr.append(res)
            curated = True
            
for i in range(int(t_psi_g_u_implies_u/5)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_g',tree))>0 and len(re.findall(r"'RULE', 'eq'",tree)) and len(re.findall(r'omega_and_omega', tree))==0 and len(re.findall(r'psi_implies_psi', tree))==0:
            curated_arr.append(res)
            curated = True
            
for i in range(int(t_psi_g_u_implies_u/5)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_g',tree))>0 and len(re.findall(r"'RULE', 'd_gt'",tree)) and len(re.findall(r'omega_and_omega', tree))==0 and len(re.findall(r'psi_implies_psi', tree))==0:
            curated_arr.append(res)
            curated = True
            
for i in range(int(t_psi_g_u_implies_u/5)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_g',tree))>0 and len(re.findall(r"'RULE', 'd_lt'",tree)) and len(re.findall(r'omega_and_omega', tree))==0 and len(re.findall(r'psi_implies_psi', tree))==0:
            curated_arr.append(res)
            curated = True
            
for i in range(int(t_psi_fg_u_and_u/5)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_fg',tree))>0 and len(re.findall(r"'RULE', 'gt'",tree)) and len(re.findall(r"omega_and_omega",tree))==0 and len(re.findall(r"psi_implies_psi",tree))==0:
            curated_arr.append(res)
            curated = True
            
for i in range(int(t_psi_fg_u_and_u/5)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_fg',tree))>0 and len(re.findall(r"'RULE', 'lt'",tree)) and len(re.findall(r"omega_and_omega", tree))==0 and len(re.findall(r"psi_implies_psi", tree))==0:
            curated_arr.append(res)
            curated = True
            
for i in range(int(t_psi_fg_u_and_u/5)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_fg',tree))>0 and len(re.findall(r"'RULE', 'eq'",tree)) and len(re.findall(r'omega_and_omega', tree))==0 and len(re.findall(r'psi_implies_psi', tree))==0:
            curated_arr.append(res)
            curated = True
            
for i in range(int(t_psi_fg_u_and_u/5)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_fg',tree))>0 and len(re.findall(r"'RULE', 'd_lt'",tree)) and len(re.findall(r'omega_and_omega', tree))==0 and len(re.findall(r'psi_implies_psi', tree))==0:
            curated_arr.append(res)
            curated = True
            
for i in range(int(t_psi_fg_u_and_u/5)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_fg',tree))>0 and len(re.findall(r"'RULE', 'd_eq'",tree)) and len(re.findall(r'omega_and_omega', tree))==0 and len(re.findall(r'psi_implies_psi', tree))==0:
            curated_arr.append(res)
            curated = True

for i in range(int(t_psi_f_u_and_u/5)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_f',tree))>0 and len(re.findall(r"'RULE', 'gt'",tree)) and len(re.findall(r"omega_and_omega",tree))==0 and len(re.findall(r"psi_implies_psi",tree))==0:
            curated_arr.append(res)
            curated = True
            
for i in range(int(t_psi_f_u_and_u/5)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_f',tree))>0 and len(re.findall(r"'RULE', 'lt'",tree)) and len(re.findall(r"omega_and_omega", tree))==0 and len(re.findall(r"psi_implies_psi", tree))==0:
            curated_arr.append(res)
            curated = True
            
for i in range(int(t_psi_f_u_and_u/5)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_f',tree))>0 and len(re.findall(r"'RULE', 'eq'",tree)) and len(re.findall(r'omega_and_omega', tree))==0 and len(re.findall(r'psi_implies_psi', tree))==0:
            curated_arr.append(res)
            curated = True
            
for i in range(int(t_psi_f_u_and_u/5)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_f',tree))>0 and len(re.findall(r"'RULE', 'd_gt'",tree)) and len(re.findall(r'omega_and_omega', tree))==0 and len(re.findall(r'psi_implies_psi', tree))==0:
            curated_arr.append(res)
            curated = True
            
for i in range(int(t_psi_f_u_and_u/5)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_f',tree))>0 and len(re.findall(r"'RULE', 'd_eq'",tree)) and len(re.findall(r'omega_and_omega', tree))==0 and len(re.findall(r'psi_implies_psi', tree))==0:
            curated_arr.append(res)
            curated = True

for i in range(int(t_psi_g_u_and_u/5)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_g',tree))>0 and len(re.findall(r"'RULE', 'gt'",tree)) and len(re.findall(r"omega_and_omega",tree))==0 and len(re.findall(r"psi_implies_psi",tree))==0:
            curated_arr.append(res)
            curated = True
            
for i in range(int(t_psi_g_u_and_u/5)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_g',tree))>0 and len(re.findall(r"'RULE', 'lt'",tree)) and len(re.findall(r"omega_and_omega", tree))==0 and len(re.findall(r"psi_implies_psi", tree))==0:
            curated_arr.append(res)
            curated = True
            
for i in range(int(t_psi_g_u_and_u/5)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_g',tree))>0 and len(re.findall(r"'RULE', 'eq'",tree)) and len(re.findall(r'omega_and_omega', tree))==0 and len(re.findall(r'psi_implies_psi', tree))==0:
            curated_arr.append(res)
            curated = True
            
for i in range(int(t_psi_g_u_and_u/5)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_g',tree))>0 and len(re.findall(r"'RULE', 'd_gt'",tree)) and len(re.findall(r'omega_and_omega', tree))==0 and len(re.findall(r'psi_implies_psi', tree))==0:
            curated_arr.append(res)
            curated = True
            
for i in range(int(t_psi_g_u_and_u/5)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_g',tree))>0 and len(re.findall(r"'RULE', 'd_lt'",tree)) and len(re.findall(r'omega_and_omega', tree))==0 and len(re.findall(r'psi_implies_psi', tree))==0:
            curated_arr.append(res)
            curated = True

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
            
for i in range(int(t_psi_f_u/5)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_f',tree))>0 and len(re.findall(r"u_and_u",tree))==0 and len(re.findall(r'u_implies_u',tree))==0 and len(re.findall(r"'RULE', 'd_eq'",tree)) and len(re.findall(r'omega_and_omega', tree))==0 and len(re.findall(r'psi_implies_psi', tree))==0:
            curated_arr.append(res)
            curated = True

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
            curated = True 

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

for i in range(int(t_psi_implies_psi_f_u_implies_u/5)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_f',tree))>0 and len(re.findall(r"u_implies_u",tree))>0 and len(re.findall(r"'RULE', 'd_eq'",tree)) and len(re.findall(r'psi_implies_psi', tree))>0:
            curated_arr.append(res)
            curated = True

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
            curated_arr.append(res)
            curated = True

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

for i in range(int(t_psi_implies_psi_f_u_and_u/5)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_f',tree))>0 and len(re.findall(r"u_and_u",tree))>0 and len(re.findall(r"'RULE', 'd_eq'",tree)) and len(re.findall(r'psi_implies_psi', tree))>0:
            curated_arr.append(res)
            curated = True

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

for i in range(int(t_psi_implies_psi_f_u/5)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_f',tree))>0 and len(re.findall(r"u_and_u",tree))==0 and len(re.findall(r'u_implies_u',tree))==0 and len(re.findall(r"'RULE', 'd_eq'",tree)) and len(re.findall(r'psi_implies_psi', tree))>0:
            curated_arr.append(res)
            curated = True

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

for i in range(int(t_omega_and_omega_fg_u_implies_u/5)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_fg',tree))>0 and len(re.findall(r"'RULE', 'gt'",tree))>0 and len(re.findall(r"omega_and_omega",tree))>0:
            curated_arr.append(res)
            curated = True
            
for i in range(int(t_omega_and_omega_fg_u_implies_u/5)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_fg',tree))>0 and len(re.findall(r"'RULE', 'lt'",tree))>0 and len(re.findall(r"omega_and_omega", tree))>0:
            curated_arr.append(res)
            curated = True
            
for i in range(int(t_omega_and_omega_fg_u_implies_u/5)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_fg',tree))>0 and len(re.findall(r"'RULE', 'eq'",tree))>0 and len(re.findall(r'omega_and_omega', tree))>0:
            curated_arr.append(res)
            curated = True

for i in range(int(t_omega_and_omega_fg_u_implies_u/5)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_fg',tree))>0 and len(re.findall(r"'RULE', 'd_lt'",tree))>0 and len(re.findall(r'omega_and_omega', tree))>0:
            curated_arr.append(res)
            curated = True
            
for i in range(int(t_omega_and_omega_fg_u_implies_u/5)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_fg',tree))>0 and len(re.findall(r"'RULE', 'd_eq'",tree))>0 and len(re.findall(r'omega_and_omega', tree))>0:
            curated_arr.append(res)
            curated = True
            
for i in range(int(t_omega_and_omega_f_u_implies_u/5)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_f',tree))>0 and len(re.findall(r"'RULE', 'gt'",tree))>0 and len(re.findall(r"omega_and_omega",tree))>0:
            curated_arr.append(res)
            curated = True
            
for i in range(int(t_omega_and_omega_f_u_implies_u/5)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_f',tree))>0 and len(re.findall(r"'RULE', 'lt'",tree))>0 and len(re.findall(r"omega_and_omega", tree))>0:
            curated_arr.append(res)
            curated = True
            
for i in range(int(t_omega_and_omega_f_u_implies_u/5)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_f',tree))>0 and len(re.findall(r"'RULE', 'eq'",tree))>0 and len(re.findall(r'omega_and_omega', tree))>0:
            curated_arr.append(res)
            curated = True
            
for i in range(int(t_omega_and_omega_f_u_implies_u/5)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_f',tree))>0 and len(re.findall(r"'RULE', 'd_gt'",tree))>0 and len(re.findall(r'omega_and_omega', tree))>0:
            curated_arr.append(res)
            curated = True

for i in range(int(t_omega_and_omega_f_u_implies_u/5)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_f',tree))>0 and len(re.findall(r"'RULE', 'd_eq'",tree))>0 and len(re.findall(r'omega_and_omega', tree))>0:
            curated_arr.append(res)
            curated = True

for i in range(int(t_omega_and_omega_g_u_implies_u/5)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_g',tree))>0 and len(re.findall(r"'RULE', 'gt'",tree))>0 and len(re.findall(r"omega_and_omega",tree))>0:
            curated_arr.append(res)
            curated = True
            
for i in range(int(t_omega_and_omega_g_u_implies_u/5)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_g',tree))>0 and len(re.findall(r"'RULE', 'lt'",tree))>0 and len(re.findall(r"omega_and_omega", tree))>0:
            curated_arr.append(res)
            curated = True
            
for i in range(int(t_omega_and_omega_g_u_implies_u/5)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_g',tree))>0 and len(re.findall(r"'RULE', 'eq'",tree))>0 and len(re.findall(r'omega_and_omega', tree))>0:
            curated_arr.append(res)
            curated = True
            
for i in range(int(t_omega_and_omega_g_u_implies_u/5)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_g',tree))>0 and len(re.findall(r"'RULE', 'd_gt'",tree))>0 and len(re.findall(r'omega_and_omega', tree))>0:
            curated_arr.append(res)
            curated = True
            
for i in range(int(t_omega_and_omega_g_u_implies_u/5)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_g',tree))>0 and len(re.findall(r"'RULE', 'd_lt'",tree))>0 and len(re.findall(r'omega_and_omega', tree))>0:
            curated_arr.append(res)
            curated = True

for i in range(int(t_omega_and_omega_fg_u_and_u/5)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_fg',tree))>0 and len(re.findall(r"'RULE', 'gt'",tree))>0 and len(re.findall(r"omega_and_omega",tree))>0:
            curated_arr.append(res)
            curated = True
            
for i in range(int(t_omega_and_omega_fg_u_and_u/5)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_fg',tree))>0 and len(re.findall(r"'RULE', 'lt'",tree))>0 and len(re.findall(r"omega_and_omega", tree))>0:
            curated_arr.append(res)
            curated = True
            
for i in range(int(t_omega_and_omega_fg_u_and_u/5)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_fg',tree))>0 and len(re.findall(r"'RULE', 'eq'",tree))>0 and len(re.findall(r'omega_and_omega', tree))>0:
            curated_arr.append(res)
            curated = True

for i in range(int(t_omega_and_omega_fg_u_and_u/5)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_fg',tree))>0 and len(re.findall(r"'RULE', 'd_lt'",tree))>0 and len(re.findall(r'omega_and_omega', tree))>0:
            curated_arr.append(res)
            curated = True

for i in range(int(t_omega_and_omega_fg_u_and_u/5)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_fg',tree))>0 and len(re.findall(r"'RULE', 'd_eq'",tree))>0 and len(re.findall(r'omega_and_omega', tree))>0:
            curated_arr.append(res)
            curated = True

for i in range(int(t_omega_and_omega_f_u_and_u/5)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_f',tree))>0 and len(re.findall(r"'RULE', 'gt'",tree))>0 and len(re.findall(r"omega_and_omega",tree))>0:
            curated_arr.append(res)
            curated = True
            
for i in range(int(t_omega_and_omega_f_u_and_u/5)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_f',tree))>0 and len(re.findall(r"'RULE', 'lt'",tree))>0 and len(re.findall(r"omega_and_omega", tree))>0:
            curated_arr.append(res)
            curated = True
            
for i in range(int(t_omega_and_omega_f_u_and_u/5)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_f',tree))>0 and len(re.findall(r"'RULE', 'eq'",tree))>0 and len(re.findall(r'omega_and_omega', tree))>0:
            curated_arr.append(res)
            curated = True
            
for i in range(int(t_omega_and_omega_f_u_and_u/5)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_f',tree))>0 and len(re.findall(r"'RULE', 'd_gt'",tree))>0 and len(re.findall(r'omega_and_omega', tree))>0:
            curated_arr.append(res)
            curated = True

for i in range(int(t_omega_and_omega_f_u_and_u/5)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_f',tree))>0 and len(re.findall(r"'RULE', 'd_eq'",tree))>0 and len(re.findall(r'omega_and_omega', tree))>0:
            curated_arr.append(res)
            curated = True

for i in range(int(t_omega_and_omega_g_u_and_u/5)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_g',tree))>0 and len(re.findall(r"'RULE', 'gt'",tree))>0 and len(re.findall(r"omega_and_omega",tree))>0:
            curated_arr.append(res)
            curated = True
            
for i in range(int(t_omega_and_omega_g_u_and_u/5)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_g',tree))>0 and len(re.findall(r"'RULE', 'lt'",tree))>0 and len(re.findall(r"omega_and_omega", tree))>0:
            curated_arr.append(res)
            curated = True
            
for i in range(int(t_omega_and_omega_g_u_and_u/5)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_g',tree))>0 and len(re.findall(r"'RULE', 'eq'",tree))>0 and len(re.findall(r'omega_and_omega', tree))>0:
            curated_arr.append(res)
            curated = True
            
for i in range(int(t_omega_and_omega_g_u_and_u/5)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_g',tree))>0 and len(re.findall(r"'RULE', 'd_gt'",tree))>0 and len(re.findall(r'omega_and_omega', tree))>0:
            curated_arr.append(res)
            curated = True
            
for i in range(int(t_omega_and_omega_g_u_and_u/5)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_g',tree))>0 and len(re.findall(r"'RULE', 'd_lt'",tree))>0 and len(re.findall(r'omega_and_omega', tree))>0:
            curated_arr.append(res)
            curated = True

for i in range(int(t_omega_and_omega_fg_u/5)): 
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

for i in range(int(t_omega_and_omega_f_u/5)):
    curated = False
    while not curated:
        res = random.choice(large_dataset)
        tree = str(parser.parse(res))
        if len(re.findall(r'temp_op_f',tree))>0 and len(re.findall(r"u_and_u",tree))==0 and len(re.findall(r'u_implies_u',tree))==0 and len(re.findall(r"'RULE', 'd_eq'",tree)) and len(re.findall(r'omega_and_omega', tree))>0:
            curated_arr.append(res)
            curated = True

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

try:
    with open(f'./pkl/curated_dataset.pkl', 'wb') as results:
        pickle.dump(curated_arr, results)
        print(curated_arr)
except Exception as e:
    print(e)