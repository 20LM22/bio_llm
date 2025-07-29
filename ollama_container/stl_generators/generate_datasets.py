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
large_dataset

# requirements
percent_temporal = 0.7
percent_nontemporal = 1 - percent_temporal

percent_and = 0.5
percent_implies = 0.3

percent_u = 1/6

curated_size = 500
curated_arr = []

curated = False

while not curated:
    # sample 500
    for i in range(curated_size):
        curated_arr.append(stl_base_instance.sample('omega'))


    print('starting next iteration')
    fg_count = 0
    g_count = 0
    f_count = 0
    gt_count = 0
    lt_count = 0
    eq_count = 0
    d_gt_count = 0
    d_lt_count = 0
    d_eq_count = 0
    c_hi_count = 0
    c_mid_count = 0
    c_lo_count = 0
    implies_count = 0
    and_count = 0
    temporal_count = 0
    der_count = 0
    print('all counts reset, right before sample iteration')

    # evaluate whether sizes are met
    for sample in curated_arr:

        fg_found = True if len(re.findall(r'eventually\[\d+,\d+\]globally\(',sample)) + len(re.findall(r'eventually\[\d+,∞\]globally\(', sample)) + len(re.findall(r'eventually\[∞,\d+\]globally\(', sample)) + len(re.findall(r'eventually\[∞,∞\]globally\(', sample)) > 0 else False
        f_found = True if len(re.findall(r'eventually\[\d+,\d+\]\(',sample)) + len(re.findall(r'eventually\[\d+,∞\]\(', sample)) + len(re.findall(r'eventually\[∞,\d+\]\(', sample)) + len(re.findall(r'eventually\[∞,∞\]\(', sample)) > 0 else False
        g_found = True if len(re.findall(r'globally\[\d+,\d+\]\(',sample)) + len(re.findall(r'globally\[\d+,∞\]\(', sample)) + len(re.findall(r'globally\[∞,\d+\]\(', sample)) + len(re.findall(r'globally\[∞,∞\]\(', sample)) > 0 else False

        c_hi_found = True if len(re.findall(r'c\(high\)', sample)) > 0 else False
        c_mid_found = True if len(re.findall(r'c\(mid\)', sample)) > 0 else False
        c_lo_found = True if len(re.findall(r'c\(low\)', sample)) > 0 else False

        implies_found = True if len(re.findall(r'implies', sample)) > 0 else False
        and_found = True if len(re.findall(r'and', sample)) > 0 else False

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

        gt_found = True if gt_count_f > 0 else False
        lt_found = True if lt_count_f > 0 else False
        eq_found = True if eq_count_f > 0 else False
        d_gt_found = True if d_gt_count_f > 0 else False
        d_lt_found = True if d_lt_count_f > 0 else False
        d_eq_found = True if d_eq_count_f > 0 else False

        """
        print(f"sample is: {sample}")
        print(f'FG: {fg_found}')
        print(f'G: {g_found}')
        print(f'F: {f_found}')
        print(f'>: {gt_found}')
        print(f'<: {lt_found}')
        print(f'=: {eq_found}')
        print(f'd >: {d_gt_found}')
        print(f'd <: {d_lt_found}')
        print(f'd =: {d_eq_found}')
        print(f'c(high): {c_hi_found}')
        print(f'c(mid): {c_mid_found}')
        print(f'c(low): {c_lo_found}')
        print(f'implies: {implies_found}')
        print(f'and: {and_found}\n')
        """

        fg_count += 1 if fg_found else 0
        g_count += 1 if g_found else 0
        f_count += 1 if f_found else 0
        gt_count += 1 if gt_found else 0
        lt_count += 1 if lt_found else 0
        eq_count += 1 if eq_found else 0
        d_gt_count += 1 if d_gt_found else 0
        d_lt_count += 1 if d_lt_found else 0
        d_eq_count += 1 if d_eq_found else 0
        c_hi_count += 1 if c_hi_found else 0
        c_mid_count += 1 if c_mid_found else 0
        c_lo_count += 1 if c_lo_found else 0
        implies_count += 1 if implies_found else 0
        and_count += 1 if and_found else 0
        temporal_count += 1 if fg_count or g_count or f_count else 0
        der_count += 1 if d_gt_found or d_lt_found or d_eq_found else 0
    
    print('just finished sample iteration')

    print(f'fg_count dksfjslkdjsdljflsdjfl: {fg_count}')
    print(f'g_count dksfjslkdjsdljflsdjfl: {g_count}')
    print(f'f_count dksfjslkdjsdljflsdjfl: {f_count}')
    print(f'gt_count dksfjslkdjsdljflsdjfl: {gt_count}')
    print(f'lt_count dksfjslkdjsdljflsdjfl: {lt_count}')
    print(f'eq_count dksfjslkdjsdljflsdjfl: {eq_count}')
    print(f'd_gt_count dksfjslkdjsdljflsdjfl: {d_gt_count}')
    print(f'd_lt_count dksfjslkdjsdljflsdjfl: {d_lt_count}')
    print(f'd_eq_count dksfjslkdjsdljflsdjfl: {d_eq_count}')

    print(f'curated size is: {curated_size}')
    
    # done looping through samples

    # temporal should be split evenly between the 3
    fg_per = fg_count/curated_size
    f_per = f_count/curated_size
    g_per = g_count/curated_size

    temporal_split_s = True if abs(fg_per - f_per) < 0.02 and abs(fg_per - g_per) < 0.02 and abs(g_per - f_per) < 0.02 else False
    temporal_s = True if abs(temporal_count/curated_size - 0.70) < 0.02 else False
    """
    print(f'temporal_count/curated_size: {temporal_count/curated_size}')
    print(f'fg_per: {fg_per}')
    print(f'g_per: {g_per}')
    print(f'f_per: {f_per}')
    """

    # and, implies, u-split
    and_s = True if abs(and_count/curated_size - 0.5) < 0.02 else False
    implies_s = True if abs(implies_count/curated_size - 0.4) < 0.02 else False
    # print(f'implies_count/curated_size: {implies_count/curated_size}')
    # print(f'and_count/curated_size: {and_count/curated_size}')

    u_split_s = True if abs(gt_count/curated_size - 1/6) < 0.02 and abs(lt_count/curated_size - 1/6) < 0.02 and abs(eq_count/curated_size - 1/6) < 0.02 and abs(d_gt_count/curated_size - 1/6) < 0.02 and abs(d_lt_count/curated_size - 1/6) < 0.02 and abs(d_eq_count/curated_size - 1/6) < 0.02 else False
    """
    print(f'gt_count/curated_size: {gt_count/curated_size}')
    print(f'lt_count/curated_size: {lt_count/curated_size}')
    print(f'eq_count/curated_size: {eq_count/curated_size}')
    print(f'd_gt_count/curated_size: {d_gt_count/curated_size}')
    print(f'd_lt_count/curated_size: {d_lt_count/curated_size}')
    print(f'd_eq_count/curated_size: {d_eq_count/curated_size}')
    """

    # derivative split
    der_s = True if abs(der_count/curated_size - 0.5) < 0.02 else False
    """
    print(f'der_count/curated_size: {der_count/curated_size}')
    print('no good')
    print(f'temporal_split_s: {temporal_split_s}')
    print(f'temporal_s: {temporal_s}')
    print(f'u_split_s: {u_split_s}')
    print(f'and_s: {and_s}')
    print(f'implies_s: {implies_s}')
    print(f'der_s: {der_s}')
    """

    print('done with one iteration')

    if temporal_split_s and temporal_s and u_split_s and and_s and implies_s and der_s:
        curated = True

