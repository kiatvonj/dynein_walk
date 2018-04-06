#! /usr/bin/env python3

from __future__ import division
import numpy as np
import time, signal, sys, os, matplotlib, subprocess, re

if 'show' not in sys.argv:
    matplotlib.use('Agg')

import argparse
import datetime
import dynein.draw.cartoon as cartoon
import matplotlib.pyplot as plt
from matplotlib import gridspec
from matplotlib.patches import Rectangle

import io

EPSILON = 1e-7

def equal(f1, f2):
    return abs(f1-f2) < EPSILON

parser = argparse.ArgumentParser(description = 'script to generate various histograms from stepping data.')

parser.add_argument('-b', '--basename', dest = 'custom_basename', action='store', type= str,
                    default="", help='data file basename')

args = parser.parse_args()

parameters_filename = ""
if args.custom_basename != "":
    for fname in os.listdir("data/"):
        if os.path.isfile("data/" + fname):
            if ("paper_" + args.custom_basename + "_stepping_parameters.tex" in fname):
                parameters_filename = "data/" + fname
                break
    assert(parameters_filename != "")
else:
    parameters_filename = 'data/paper_static_stepping_parameters.tex'

run_conditions = open(parameters_filename).read()
raw_run_conditions = run_conditions.replace("\n", " ").replace("\\\\", "\\")

data_files = []
if args.custom_basename != "":
    for fname in os.listdir("data/"):
        if os.path.isfile("data/" + fname):
            if ("paper_" + args.custom_basename + "_stepping_data" in fname):
                data_files.append("data/" + fname)
else:
    for fname in os.listdir("data/"):
        if os.path.isfile("data/" + fname):
            if ("paper_static_stepping_data" in fname):
                data_files.append("data/" + fname)

if len(data_files) == 0:
    if args.custom_basename != "":
        print("No files of form paper_" + args.custom_basename + "_stepping_data" "*.txt found. Exiting.")
    else:
        print("Error, no files of form data/paper_static_stepping_data*.txt found. Exiting.")
    exit(1)

step_times = []
onebound_times = []
bothbound_times = []
step_lengths = []
initial_displacements = []
step_times = []
run_velocities = []

alternating_passing = 0
alternating_not_passing = 0
not_alternating_passing = 0
not_alternating_not_passing = 0

leading_foot_steps = 0
trailing_foot_steps = 0

for data_file in data_files:
    data = np.loadtxt(data_file, dtype = np.float64)
    if len(data) < 3 or str(type(data[0])) == "<type 'numpy.float64'>":
        continue

    bind_times = np.array(data[:,1])
    unbind_times = np.array(data[:,0])
    near_foot_positions = np.around(np.array(data[:,2]), decimals=12)  #need to figure out why fixing number of decimals is necessary
    far_foot_positions = np.around(np.array(data[:,3]), decimals=12)
    near_step_lens = near_foot_positions[1:] - near_foot_positions[:-1]  #reduces total length by one. Will include 0 step lengths
    far_step_lens = far_foot_positions[1:] - far_foot_positions[:-1]

    for s in range(1,len(near_foot_positions)):
        # print("near foot positions s-1, s: ", near_foot_positions[s-1], near_foot_positions[s])
        # print("far foot positions s-1, s: ", far_foot_positions[s-1], far_foot_positions[s])
        assert(equal(near_foot_positions[s-1],near_foot_positions[s]) or equal(far_foot_positions[s-1],far_foot_positions[s]))
        if equal(near_foot_positions[s-1],near_foot_positions[s]) and equal(far_foot_positions[s-1],far_foot_positions[s]):
            continue

        if not equal(near_foot_positions[s-1],near_foot_positions[s]):
            step_lengths.append(data[s,2]-data[s-1,2])
            initial_displacements.append(data[s-1,2]-data[s-1,3])
        elif not equal(far_foot_positions[s-1],far_foot_positions[s]):
            step_lengths.append(data[s,3]-data[s-1,3])
            initial_displacements.append(data[s-1,3]-data[s-1,2])

        onebound_times = np.concatenate((onebound_times, [bind_times[s]-unbind_times[s]]))
        bothbound_times = np.concatenate((bothbound_times, [unbind_times[s]-bind_times[s-1]]))
        step_times = np.concatenate((step_times, onebound_times + bothbound_times))

    run_velocities.append((data[-1,2] + data[-1,2]) / 2 / data[-1,1])

    assert(len(near_foot_positions) > 10)
    for s in range(2, len(near_foot_positions)):
        if near_foot_positions[s-1] < far_foot_positions[s-1]:
            trailing_foot = near_foot_positions
            leading_foot = far_foot_positions
        else:
            trailing_foot = far_foot_positions
            leading_foot = near_foot_positions
        if not equal(near_foot_positions[s], near_foot_positions[s-1]) and not equal(far_foot_positions[s], far_foot_positions[s-1]):
            print("Error, both feet moved in a step.")
            exit(1)
        if not equal(trailing_foot[s], trailing_foot[s-1]): #must've been a leading foot step
            leading_foot_steps += 1
            if not equal(trailing_foot[s-1], trailing_foot[s-2]): # not alternating, the last was the same foot
                # the leading foot moved twice in a row, that makes this "not alternating"
                not_alternating_not_passing += 1
            else:
                # It is alternating because leading foot moved, but before that the other foot moved.
                alternating_not_passing += 1
        else: # must've been a trailing foot step
            trailing_foot_steps += 1
            if equal(trailing_foot[s-1], trailing_foot[s-2]): # alternating, other foot moved last time
                if trailing_foot[s] > leading_foot[s]:
                    not_alternating_passing += 1
                else:
                    not_alternating_not_passing += 1
            else:
                if trailing_foot[s] > leading_foot[s]:
                    alternating_passing += 1
                else:
                    alternating_not_passing += 1

num_steps = len(step_lengths)

t_step = []
t_ob = []
t_bb = []
t_ob_uncertainty = []
t_bb_uncertainty = []
t_proc = []

t_step.append(np.mean(step_times))
t_ob.append(np.mean(onebound_times))
t_bb.append(np.mean(bothbound_times))
t_proc.append(t_step[-1]*t_bb[-1]/t_ob[-1])

t_ob_uncertainty.append(np.std(onebound_times)/np.sqrt(num_steps)*1.645) # 95% chance of true average being 1.645 stdevs from the sample average
t_bb_uncertainty.append(np.std(bothbound_times)/np.sqrt(num_steps)*1.645)

#step length histogram

fig = plt.figure()
plt.rc('text', usetex=True)

weihong_step_lengths = np.array([])
weihong_step_lengths = np.append(weihong_step_lengths, [-35]*3)
weihong_step_lengths = np.append(weihong_step_lengths, [-25]*3)
weihong_step_lengths = np.append(weihong_step_lengths, [-22]*4)
weihong_step_lengths = np.append(weihong_step_lengths, [-19]*10)
weihong_step_lengths = np.append(weihong_step_lengths, [-16]*15)
weihong_step_lengths = np.append(weihong_step_lengths, [-13]*30)
weihong_step_lengths = np.append(weihong_step_lengths, [-10]*62)
weihong_step_lengths = np.append(weihong_step_lengths, [-7]*80)
weihong_step_lengths = np.append(weihong_step_lengths, [-4]*67)
weihong_step_lengths = np.append(weihong_step_lengths, [2]*94)
weihong_step_lengths = np.append(weihong_step_lengths, [5]*94)
weihong_step_lengths = np.append(weihong_step_lengths, [8]*209)
weihong_step_lengths = np.append(weihong_step_lengths, [11]*152)
weihong_step_lengths = np.append(weihong_step_lengths, [14]*128)
weihong_step_lengths = np.append(weihong_step_lengths, [17]*80)
weihong_step_lengths = np.append(weihong_step_lengths, [20]*67)
weihong_step_lengths = np.append(weihong_step_lengths, [23]*35)
weihong_step_lengths = np.append(weihong_step_lengths, [26]*24)
weihong_step_lengths = np.append(weihong_step_lengths, [29]*13)
weihong_step_lengths = np.append(weihong_step_lengths, [32]*11)
weihong_step_lengths = np.append(weihong_step_lengths, [35]*8)
weihong_step_lengths = np.append(weihong_step_lengths, [35]*4)
weihong_step_lengths = np.append(weihong_step_lengths, [38]*2)

if len(step_lengths) == 0:
    print("No steps to put in histogram!")

plt.hist(weihong_step_lengths, bins=20, alpha=0.5, label="Experiment", normed=True, stacked=True)
if (len(step_lengths) > 0):
    plt.hist(step_lengths, bins=20, alpha=0.5, label="Model", normed=True, stacked=True)

plt.scatter([np.mean(step_lengths)], [0], label=raw_run_conditions + r'$\overline{\Delta x} = ' + str(np.around(np.mean(step_lengths), decimals=2)) + r'$ \textit{nm}')

plt.legend(loc="upper right")
plt.xlabel("Step length (nm)")
plt.ylabel("Frequency")

plt.gcf().suptitle(
    raw_run_conditions +
    r' $k_{b}: \kb, k_{ub}: \kub, cb: \cb, cm: \cm, ct: \ct, runtime: \runtime$',
    fontsize=14)

plt.savefig("plots/stepping_length_histogram.pdf", format="pdf")
plt.close(fig)

#step time histogram
fig = plt.figure(figsize=(8, 8), dpi=300)
plt.rc('text', usetex=True)

gs = gridspec.GridSpec(4, 1, height_ratios=[1, 1, 1, 1])
ax0 = fig.add_subplot(gs[0])
ax1 = fig.add_subplot(gs[1])
ax2 = fig.add_subplot(gs[2])
ax3 = fig.add_subplot(gs[3])

if len(step_times) > 0:
    ax0.hist(step_times, bins=np.logspace(np.log10(1e-10),np.log10(1e-2), 50))
    ax1.hist(onebound_times, bins=np.logspace(np.log10(1e-10),np.log10(1e-2), 50))
    ax2.hist(bothbound_times, bins=np.logspace(np.log10(1e-10),np.log10(1e-2), 50))
    ax3.hist(run_velocities, bins=50)

ax0.set_title("Step times")
ax0.set_ylabel("Frequency")
ax0.set_xscale('log')
# ax0.ticklabel_format(style='sci', axis='x', scilimits=(0,0))

ax1.set_title("onebound times (theory: 6e-5)")
ax1.set_ylabel("Frequency")
ax1.set_xscale('log')
# ax1.ticklabel_format(style='sci', axis='x', scilimits=(0,0))

ax2.set_title("bothbound times (theory: 0.011s)")
ax2.set_xlabel("Step time (s)")
ax2.set_ylabel("Frequency")
ax2.set_xscale('log')
# ax2.ticklabel_format(style='sci', axis='x', scilimits=(0,0))

ax3.set_title("velocities (theory: 700nm/s)")
ax3.set_xlabel("velocity (nm/s)")
ax3.set_ylabel("Frequency")

plt.gcf().suptitle(
    raw_run_conditions +
    r' $k_{b}: \kb, k_{ub}: \kub, cb: \cb, cm: \cm, ct: \ct, runtime: \runtime$',
    fontsize=14)

plt.subplots_adjust(hspace=0.6)

plt.show()
plt.savefig("plots/stepping_time_histogram.pdf", format="pdf")
plt.close(fig)

# OB_time vs step_length scatter
assert len(onebound_times) == len(step_lengths)
fig = plt.figure()
plt.scatter(onebound_times, step_lengths)
plt.gca().set_xscale('log')
plt.xlabel("Onebound time (s)")
plt.ylabel("Step length (nm)")

plt.gca().set_xlim((1e-7, 1e-2))

plt.gcf().suptitle(
    raw_run_conditions +
    r' $k_{b}: \kb, k_{ub}: \kub, cb: \cb, cm: \cm, ct: \ct, runtime: \runtime$',
    fontsize=14)

plt.savefig("plots/ob-vs-length-scatter.pdf", format="pdf")
plt.close(fig)

# BB_time vs step_length scatter
assert len(bothbound_times) == len(step_lengths)
fig = plt.figure()
plt.scatter(bothbound_times, step_lengths)
plt.gca().set_xscale('log')
plt.xlabel("Bothbound time (s)")
plt.ylabel("Step length (nm)")

plt.gca().set_xlim((1e-5, 1))

plt.gcf().suptitle(
    raw_run_conditions +
    r' $k_{b}: \kb, k_{ub}: \kub, cb: \cb, cm: \cm, ct: \ct, runtime: \runtime$',
    fontsize=14)

plt.savefig("plots/bb-vs-length-scatter.pdf", format="pdf")
plt.close(fig)

# initial displacement vs motor step length scatter
fig = plt.figure()
plt.scatter(initial_displacements, step_lengths)
plt.xlabel("Initial foot x-displacement (unstepping - stepping) (nm)")
plt.ylabel("Step length (nm)")

plt.gcf().suptitle(
    raw_run_conditions +
    r' $k_{b}: \kb, k_{ub}: \kub, cb: \cb, cm: \cm, ct: \ct, runtime: \runtime$',
    fontsize=14)

plt.savefig("plots/displacement_vs_step_length.pdf", format="pdf")
plt.close(fig)

fig = plt.figure(figsize=(8*.6, 6*.6), dpi=300)
plt.rc('text', usetex=True)

gs = gridspec.GridSpec(1, 3, width_ratios=[1, 1, 1])
ax1 = fig.add_subplot(gs[0])
ax2 = fig.add_subplot(gs[1])
ax3 = fig.add_subplot(gs[2])

width = 0.5

ax1.bar([0, 1], [alternating_passing + alternating_not_passing, not_alternating_passing + not_alternating_not_passing,], width)
ax1.set_ylabel('frequency')
ax1.set_xticks([0, 1])
ax1.set_xticklabels(('alternating', 'not\nalternating'), rotation=45)

ax2.bar([0, 1], [alternating_passing + not_alternating_passing, alternating_not_passing + not_alternating_not_passing,], width)
ax2.set_ylabel('frequency')
ax2.set_xticks([0, 1])
ax2.set_xticklabels(('passing', 'not passing'), rotation=45)

ax3.bar([0, 1, 2, 3], [alternating_passing, alternating_not_passing, not_alternating_passing, not_alternating_not_passing,], width)
ax3.set_ylabel('frequency')
ax3.set_xticks([0, 1, 2, 3])
ax3.set_xticklabels(('alternating,\n passing', 'alternating,\n not passing', 'not alternating,\n passing', 'not alternating,\n not passing'), rotation=45)

plt.tight_layout()

plt.savefig("plots/stepping_analysis.pdf", format="pdf")
plt.close(fig)



fig = plt.figure()

initial_displacements = np.array(initial_displacements)
indices = np.argsort(np.abs(initial_displacements))
sorted_displacements = initial_displacements[indices]

Nbin = 50
L = np.zeros(int((len(sorted_displacements)-1)/Nbin)+1)
ntrailing = np.zeros_like(L)
nleading = np.zeros_like(L)
for i in range(len(L)):
    bunch = sorted_displacements[i*Nbin:(i+1)*Nbin]
    ntrailing[i] = (bunch < 0).sum()
    nleading[i] = (bunch > 0).sum()
    L[i] = np.abs(bunch).mean()

fraction_trailing = ntrailing / (ntrailing + nleading)

fig, ax1 = plt.subplots()
ax2 = ax1.twinx()

trailing_plot = ax1.plot(L, fraction_trailing, 'o-', label="Fraction trailing")
num_hist = ax2.hist(np.abs(initial_displacements), bins=20, alpha=0.5, label="Model", normed=True, stacked=True)

ax1.set_xlabel("FIXME Initial foot x-displacement (unstepping - stepping) (nm)")
ax1.set_ylabel("Frequency")
ax2.set_ylabel("N")

# plt.legend([trailing_plot, num_hist], ["Fraction trailing", "Number"])
# ax1.legend()
# ax2.legend()
fig.legend()

plt.gcf().suptitle(
    raw_run_conditions +
    r' $k_{b}: \kb, k_{ub}: \kub, cb: \cb, cm: \cm, ct: \ct, runtime: \runtime$',
    fontsize=14)

# plt.tight_layout()

plt.savefig("plots/displacement_histogram.pdf", format="pdf")
plt.close(fig)
