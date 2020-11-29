import os 
import numpy as np
import argparse
import sys
sys.path.append("../data")
import importlib
import bb_energy_distribution
import time

params = importlib.import_module("params")

parser = argparse.ArgumentParser()
parser.add_argument("-L", "--L", type=float, help="Array of initial L", default=50)
parser.add_argument("-i", "--i", type=float, help="Increment", default=5)
parser.add_argument("-o", "--o", type=float, help="Starting value", default=1)
parser.add_argument("-u", "--kub", type=float, help="unbinding const", default=params.for_simulation['k_ub'])
parser.add_argument("-k", "--kb", type=float, help="binding const", default=params.for_simulation['k_b'])
parser.add_argument("-s", "--ks", type=float, help="sticky const", default=params.for_simulation['k_stk'])
parser.add_argument("-cb", "--cb", type=float, help="spring const binding domain", default=params.for_simulation['cb'])
parser.add_argument("-cm", "--cm", type=float, help="spring const motor domain", default=params.for_simulation['cm'])
parser.add_argument("-ct", "--ct", type=float, help="spring const tail domain", default=params.for_simulation['ct'])
parser.add_argument("--eqb", type=float, help="binding equilibrium angle", default=params.for_simulation['eqb'])
parser.add_argument("--eqmpre", type=float, help="motor pre equilibrium angle", default=params.for_simulation['eqmpre'])
parser.add_argument("--eqmpost", type=float, help="motor post equilibrium angle", default=params.for_simulation['eqmpost'])
parser.add_argument("-t", "--dt", type=float, help="dt", default=params.for_simulation['dt'])
parser.add_argument("-c", "-cancel", type=bool, help="cancel all jobs", default=False)
args = parser.parse_args()

L = args.L
i = args.i
o = args.o
k_ub = args.kub
k_b = args.kb
k_stk = args.ks

init_L = np.arange(o, L, i, dtype=int)

if args.c == True:
    for i in range(len(init_L)):
        os.system('rq cancel -J dynein-mc-{0}-{1:.2e}-{2:.2e}-{3}-{4}-{5}-{6}-{7}-{8}-{9}'.format(k_ub, k_b, k_stk, args.cb, args.cm, args.ct, args.eqb, args.eqmpre, args.eqmpost, init_L[i]))
else: 
    for i in range(len(init_L)):
        os.system('rq run -J dynein-mc-{0}-{1:.2e}-{2:.2e}-{3}-{4}-{5}-{6}-{7}-{8}-{9} -o L-{10}-{11:.2e}-{12:.2e}-{13}-{14}-{15}-{16}-{17}-{18}-{19} python3 monte_carlo_simulation.py -u {20} -k {21} -s {22} -cb {23} -cm {24} -ct {25} --eqb {26} --eqmpre {27} --eqmpost {28} -L {29}'.format(k_ub, k_b, k_stk, args.cb, args.cm, args.ct, args.eqb, args.eqmpre, args.eqmpost, init_L[i], k_ub, k_b, k_stk, args.cb, args.cm, args.ct, args.eqb, args.eqmpre, args.eqmpost, init_L[i], k_ub, k_b, k_stk, args.cb, args.cm, args.ct, args.eqb, args.eqmpre, args.eqmpost, init_L[i]))
        time.sleep(0.1)
