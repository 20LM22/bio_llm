from lark import Lark
import numpy as np
from stl2literal import STL2literal
from stl_base import STLBase
import json, csv, sys, traceback, re, logging, pickle, pandas, os

####################################################################################
# Debugging logging
####################################################################################

import logging
logging.basicConfig(filename='output.log', level=logging.DEBUG, 
                    format='%(asctime)s %(levelname)s: %(message)s')

####################################################################################
# Set up structures, parameters
####################################################################################

file_name = f'../config/config_Qwen3-1.7B.json'

with open(file_name, 'r') as f:
    params = json.load(f)

stl_base_instance = STLBase()

signals = ["IL6", "IL12", "IL1β", "IL1Ra", "TNFα", "IL8", "IFNα", "IFNβ", "SARSCoV2", "IL1RN"]

grammar = params['grammar']
parser = Lark(grammar)

# Large 5K dataset
large_dataset = []

# Obtain 5K samples
for i in range(5000):
    large_dataset.append(stl_base_instance.sample('omega'))

# for large dataset do some analysis: filter out just the smaller ones
less_than_90 = []
less_than_85 = []
less_than_80 = []
less_than_75 = []
less_than_70 = []

for i in large_dataset:
    if len(i) < 90:
        less_than_90.append(i)
    if len(i) < 85:
        less_than_85.append(i)
    if len(i) < 80:
        less_than_80.append(i)
    if len(i) < 75:
        less_than_75.append(i)
    if len(i) < 70:
        less_than_70.append(i)
                        
def print_stats(samples, name):
    s = len(samples)

    fg_count = 0
    g_count = 0
    f_count = 0
    gt_count = 0
    lt_count = 0
    eq_count = 0
    d_gt_count = 0
    d_lt_count = 0
    d_eq_count = 0
    c_hi = 0
    c_mid = 0
    c_lo = 0
    implies_count = 0
    and_count = 0

    for sample in samples:

        fg_count += 1 if len(re.findall(r'eventually\[\d+,\d+\]globally\(',sample)) + len(re.findall(r'eventually\[\d+,∞\]globally\(', sample)) + len(re.findall(r'eventually\[∞,\d+\]globally\(', sample)) + len(re.findall(r'eventually\[∞,∞\]globally\(', sample)) > 0 else 0
        f_count += 1 if len(re.findall(r'eventually\[\d+,\d+\]\(',sample)) + len(re.findall(r'eventually\[\d+,∞\]\(', sample)) + len(re.findall(r'eventually\[∞,\d+\]\(', sample)) + len(re.findall(r'eventually\[∞,∞\]\(', sample)) > 0 else 0
        g_count += 1 if len(re.findall(r'globally\[\d+,\d+\]\(',sample)) + len(re.findall(r'globally\[\d+,∞\]\(', sample)) + len(re.findall(r'globally\[∞,\d+\]\(', sample)) + len(re.findall(r'globally\[∞,∞\]\(', sample)) > 0 else 0

        c_hi += 1 if len(re.findall(r'c\(high\)', sample)) > 0 else 0
        c_mid += 1 if len(re.findall(r'c\(mid\)', sample)) > 0 else 0
        c_lo += 1 if len(re.findall(r'c\(low\)', sample)) > 0 else 0

        implies_count += 1 if len(re.findall(r'implies', sample)) > 0 else 0
        and_count += 1 if len(re.findall(r'and', sample)) > 0 else 0

        gt_count_f = 0
        lt_count_f = 0
        eq_count_f = 0
        d_gt_count_f = 0
        d_lt_count_f = 0
        d_eq_count_f = 0

        for signal in signals:
            gt_count_f += len(re.findall(rf'\({re.escape(signal)}\(t\)>',sample))
            lt_count_f += len(re.findall(rf'\({re.escape(signal)}\(t\)<',sample))
            eq_count_f += len(re.findall(rf'\({re.escape(signal)}\(t\)=',sample))
            d_gt_count_f += len(re.findall(rf'd_{re.escape(signal)}\(t\)>',sample))
            d_lt_count_f += len(re.findall(rf'd_{re.escape(signal)}\(t\)<',sample))
            d_eq_count_f += len(re.findall(rf'd_{re.escape(signal)}\(t\)=',sample))

        gt_count += 1 if gt_count_f > 0 else 0
        lt_count += 1 if lt_count_f > 0 else 0
        eq_count += 1 if eq_count_f > 0 else 0
        d_gt_count += 1 if d_gt_count_f > 0 else 0
        d_lt_count += 1 if d_lt_count_f > 0 else 0
        d_eq_count += 1 if d_eq_count_f > 0 else 0

    print(name)
    print(f'FG: {fg_count/s}')
    print(f'G: {g_count/s}')
    print(f'F: {f_count/s}')
    print(f'>: {gt_count/s}')
    print(f'<: {lt_count/s}')
    print(f'=: {eq_count/s}')
    print(f'd >: {d_gt_count/s}')
    print(f'd <: {d_lt_count/s}')
    print(f'd =: {d_eq_count/s}')
    print(f'c(high): {c_hi/s}')
    print(f'c(mid): {c_mid/s}')
    print(f'c(low): {c_lo/s}')
    print(f'implies: {implies_count/s}')
    print(f'and: {and_count/s}\n')
    return [fg_count/s, g_count/s, f_count/s, gt_count/s, lt_count/s, eq_count/s, d_gt_count/s, d_lt_count/s, d_eq_count/s, c_hi/s, c_mid/s, c_lo/s, implies_count/s, and_count/s]

data = [print_stats(less_than_90, "less than 90"),
print_stats(less_than_85, "less than 85"),
print_stats(less_than_80, "less than 80"),
print_stats(less_than_75, "less than 75"),
print_stats(less_than_70, 'less than 70')]

df = pandas.DataFrame(data, columns=['FG', 'G', 'F', '>', '<', '=', 'd >','d <','d =', 'c(high)', 'c(mid)', 'c(low)', 'implies', 'and'])
df.insert(0, 'Char cutoff', ['90', '85', '80', '75', '70'])
df.to_csv('cutoff_comparison.csv')

# Now sample from this set to get curated 500-entry dataset

