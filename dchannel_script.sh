#!/bin/bash

# python search_adv_traces.py --type=2 --trace_length=7 --dchannel_exp_type=1 --alg=1 --l_bounds 30 2 1 1 1 2 1 --u_bounds 300 10 25 1 10 10 50 --total_time=600 --pop_size=25 --n_iter=8
python search_adv_traces.py --type=2 --trace_length=11 --dchannel_exp_type=1 --alg=1 --l_bounds 30 30 2 2 1 1 1 1 1 2 1 --u_bounds 300 300 10 10 25 25 1 1 10 10 50 --total_time=600 --pop_size=25 --n_iter=8
# python search_adv_traces.py --type=2 --trace_length=15 --dchannel_exp_type=1 --alg=1 --l_bounds 30 30 30 2 2 2 1 1 1 1 1 1 1 2 1 --u_bounds 300 300 300 10 10 10 25 25 25 1 1 1 10 10 50 --total_time=600 --pop_size=25 --n_iter=8
# python search_adv_traces.py --type=2 --trace_length=19 --dchannel_exp_type=1 --alg=1 --l_bounds 30 30 30 30 2 2 2 2 1 1 1 1 1 1 1 1 1 2 1 --u_bounds 300 300 300 300 10 10 10 10 25 25 25 25 1 1 1 1 10 10 50 --total_time=600 --pop_size=25 --n_iter=8
# python search_adv_traces.py --type=2 --trace_length=23 --dchannel_exp_type=1 --alg=1 --l_bounds 30 30 30 30 30 2 2 2 2 2 1 1 1 1 1 1 1 1 1 1 1 2 1 --u_bounds 300 300 300 300 300 10 10 10 10 10 25 25 25 25 25 1 1 1 1 1 10 10 50 --total_time=600 --pop_size=25 --n_iter=8