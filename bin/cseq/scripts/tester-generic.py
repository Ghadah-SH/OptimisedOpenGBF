#!/usr/bin/env python
'''

	multi-threaded CSeq Tester for unsafe Concurrency/ files (official SV-COMP 2020 benchmarks)

	2020.04.07  using core.utils.commandpid() process spawner
	2020.04.07  forked from [SV-COMP 2020] simulation script
	2020.04.05  changed detection of unsafe/safe instances in the .yml desc
	2019.11.17  bugfix: Command.run default timeout is None (not 0)
	2019.11.17  bugfix: script no longer terminating upon hitting timelimit
	2019.11.16  timeout for witness validator set in its own commandline
	2019.11.11  a non-verified witness now means FAIL
	2019.11.11  now using external .yml file to compare against expected verification outcome
	2018.11.25  can now run on a single program
	2018.11.23  command-line options
	2018.11.09  witness checking

'''
import sys, getopt
import os, sys
from glob import glob

# default parameters
cores = 8
backend = 'cbmc'
memory = 8   # GB
timeout = 1  # s

# Minimal parameters for each program: param["file = (unwind,round)),
# except rounds=2 for wmm* (rounds=1 is enough for some, but the time difference is negligible)
params = {}
params["concurrency/ldv-linux-3.14-races/linux-3.14--drivers--media--platform--marvell-ccic--cafe_ccic.ko.cil-2.i"] = (1,1)              # n/a: tool crashes
params["concurrency/ldv-linux-3.14-races/linux-3.14--drivers--net--irda--nsc-ircc.ko.cil.i"] = (1,1)              # n/a: tool crashes
params["concurrency/ldv-linux-3.14-races/linux-3.14--drivers--net--irda--w83977af_ir.ko.cil.i"] = (1,1)              # n/a: tool crashes
params["concurrency/ldv-linux-3.14-races/linux-3.14--drivers--spi--spi-tegra20-slink.ko.cil.i"] = (1,1)              # n/a: tool crashes
params["concurrency/ldv-linux-3.14-races/linux-3.14--drivers--usb--misc--adutux.ko.cil.i"] = (1,1)              # n/a: tool crashes
params["concurrency/ldv-linux-3.14-races/linux-3.14--drivers--usb--misc--iowarrior.ko.cil.i"] = (1,1)              # n/a: tool crashes
params["concurrency/ldv-races/race-1_2-join.i"] = (1,1)
params["concurrency/ldv-races/race-1_3-join.i"] = (1,1)
params["concurrency/ldv-races/race-2_2-container_of.i"] = (1,2)
params["concurrency/ldv-races/race-2_3-container_of.i"] = (1,2)
params["concurrency/ldv-races/race-2_4-container_of.i"] = (1,2)
params["concurrency/ldv-races/race-2_5-container_of.i"] = (1,2)
params["concurrency/ldv-races/race-3_2-container_of-global.i"] = (1,2)
params["concurrency/ldv-races/race-4_2-thread_local_vars.i"] = (1,2)
params["concurrency/pthread/bigshot_p.i"] = (1,2)
params["concurrency/pthread/fib_bench-2.i"] = (5,5)
params["concurrency/pthread/fib_bench_longer-2.i"] = (6,6)
params["concurrency/pthread/fib_bench_longest-2.i"] = (11,11)
params["concurrency/pthread/lazy01.i"] = (1,1)
params["concurrency/pthread/queue.i"] = (2,2)
params["concurrency/pthread/queue_longer.i"] = (2,2)
params["concurrency/pthread/queue_longest.i"] = (2,2)
params["concurrency/pthread/reorder_2.i"] = (2,1)
params["concurrency/pthread/reorder_5.i"] = (4,1)
params["concurrency/pthread/sigma.i"] = (16,1)
params["concurrency/pthread/singleton.i"] = (1,4)
params["concurrency/pthread/stack-2.i"] = (2,1)
params["concurrency/pthread/stack_longer-1.i"] = (2,1)
params["concurrency/pthread/stack_longest-1.i"] = (2,1)
params["concurrency/pthread/stateful01-1.i"] = (1,1)
params["concurrency/pthread/triangular-2.i"] = (5,5)
params["concurrency/pthread/triangular-longer-2.i"] = (10,10)
params["concurrency/pthread/triangular-longest-2.i"] = (20,20)
params["concurrency/pthread/twostage_3.i"] = (2,1)
params["concurrency/pthread-atomic/qrcu-2.i"] = (2,2)
params["concurrency/pthread-atomic/read_write_lock-2.i"] = (1,2)
params["concurrency/pthread-C-DAC/pthread-demo-datarace-2.i"] = (20,19)
params["concurrency/pthread-complex/bounded_buffer.i"] =  (2,2)
params["concurrency/pthread-complex/elimination_backoff_stack.i"] = (1,2)  # (36000s without simplify-args, >11.5h with --simplify-args!)
params["concurrency/pthread-complex/safestack_relacy.i"] =   (3,4)           # --simplify-args  (takes 7h!))
params["concurrency/pthread-complex/workstealqueue_mutex-1.i"] = (4,3)
params["concurrency/pthread-divine/condvar_spurious_wakeup.i"] = (1,1)        # --nondet-condvar-wakeups)
params["concurrency/pthread-divine/divinefifo-bug_1w1r.i"] = (4,4)
params["concurrency/pthread-divine/one_time_barrier_2t.i"] = (2,1)
params["concurrency/pthread-divine/one_time_barrier_3t.i"] = (3,1)
params["concurrency/pthread-divine/ring_1w1r-1.i"] = (1,1)
params["concurrency/pthread-divine/ring_2w1r-2.i"] = (2,2)
params["concurrency/pthread-divine/tls_destructor_worker.i"] = (1,1)
params["concurrency/pthread-driver-races/char_generic_nvram_read_nvram_write_nvram.i"] = (1,2)
params["concurrency/pthread-driver-races/char_pc8736x_gpio_pc8736x_gpio_change_pc8736x_gpio_current.i"] = (100,2)
params["concurrency/pthread-driver-races/char_pc8736x_gpio_pc8736x_gpio_change_pc8736x_gpio_set.i"] = (100,2)
params["concurrency/pthread-driver-races/char_pc8736x_gpio_pc8736x_gpio_current_pc8736x_gpio_set.i"] = (100,2)
params["concurrency/pthread-ext/25_stack_longer-1.i"] = (1,1)
params["concurrency/pthread-ext/25_stack_longest-2.i"] = (1,1)
params["concurrency/pthread-ext/26_stack_cas_longer-1.i"] = (1,1)
params["concurrency/pthread-ext/26_stack_cas_longest-1.i"] = (1,1)
params["concurrency/pthread-ext/27_Boop_simple_vf.i"] = (1,2)
params["concurrency/pthread-ext/28_buggy_simple_loop1_vf.i"] = (1,1)
params["concurrency/pthread-ext/32_pthread5_vs.i"] = (1,2)
params["concurrency/pthread-ext/40_barrier_vf.i"] = (3,1)
params["concurrency/pthread-lit/fkp2013-1.i"] = (50,2)
params["concurrency/pthread-lit/fkp2013_variant-2.i"] = (1,2)
params["concurrency/pthread-lit/qw2004-2.i"] = (1,1)
params["concurrency/pthread-nondet/nondet-array-1.i"] = (5,4)
params["concurrency/pthread-nondet/nondet-loop-bound-1.i"] = (20,2)
params["concurrency/pthread-nondet/nondet-loop-bound-variant-1.i"] = (5,2)   # --nondet-condvar-wakeups
params["concurrency/pthread-wmm/rfi005_power.oepc.i"] = (1,1)
params["concurrency/pthread-wmm/rfi005_power.opt.i"] = (1,1)
params["concurrency/pthread-wmm/rfi005_pso.oepc.i"] = (1,1)
params["concurrency/pthread-wmm/rfi005_pso.opt.i"] = (1,1)
params["concurrency/pthread-wmm/rfi005_rmo.oepc.i"] = (1,1)
params["concurrency/pthread-wmm/rfi005_rmo.opt.i"] = (1,1)
params["concurrency/pthread-wmm/rfi005_tso.oepc.i"] = (1,1)
params["concurrency/pthread-wmm/rfi005_tso.opt.i"] = (1,1)
params["concurrency/pthread-wmm/rfi006_power.oepc.i"] = (1,1)
params["concurrency/pthread-wmm/rfi006_power.opt.i"] = (1,1)
params["concurrency/pthread-wmm/rfi006_rmo.oepc.i"] = (1,1)
params["concurrency/pthread-wmm/rfi006_rmo.opt.i"] = (1,1)
params["concurrency/pthread-wmm/rfi009_power.oepc.i"] = (1,1)
params["concurrency/pthread-wmm/rfi009_rmo.oepc.i"] = (1,1)
params["concurrency/pthread-wmm/safe000_power.oepc.i"] = (1,1)
params["concurrency/pthread-wmm/safe000_rmo.oepc.i"] = (1,1)
params["concurrency/pthread-wmm/safe000_rmo.opt.i"] = (1,1)
params["concurrency/pthread-wmm/safe001_power.oepc.i"] = (1,1)
params["concurrency/pthread-wmm/safe001_rmo.oepc.i"] = (1,1)
params["concurrency/pthread-wmm/safe002_power.oepc.i"] = (1,1)
params["concurrency/pthread-wmm/safe002_rmo.oepc.i"] = (1,1)
params["concurrency/pthread-wmm/safe006_power.oepc.i"] = (1,1)
params["concurrency/pthread-wmm/safe006_rmo.oepc.i"] = (1,1)
params["concurrency/pthread-wmm/safe006_rmo.opt.i"] = (1,1)
params["concurrency/pthread-wmm/safe007_power.oepc.i"] = (1,1)
params["concurrency/pthread-wmm/safe007_rmo.oepc.i"] = (1,1)
params["concurrency/pthread-wmm/safe007_rmo.opt.i"] = (1,1)
params["concurrency/pthread-wmm/safe009_power.oepc.i"] = (1,1)
params["concurrency/pthread-wmm/safe009_rmo.oepc.i"] = (1,1)
params["concurrency/pthread-wmm/safe012_power.oepc.i"] = (1,1)
params["concurrency/pthread-wmm/safe012_rmo.oepc.i"] = (1,1)
params["concurrency/pthread-wmm/safe014_power.oepc.i"] = (1,1)
params["concurrency/pthread-wmm/safe014_power.opt.i"] = (1,1)
params["concurrency/pthread-wmm/safe014_rmo.oepc.i"] = (1,1)
params["concurrency/pthread-wmm/safe015_power.oepc.i"] = (1,1)
params["concurrency/pthread-wmm/safe016_power.oepc.i"] = (1,1)
params["concurrency/pthread-wmm/safe016_rmo.oepc.i"] = (1,1)
params["concurrency/pthread-wmm/safe018_power.oepc.i"] = (1,1)
params["concurrency/pthread-wmm/safe018_rmo.oepc.i"] = (1,1)
params["concurrency/pthread-wmm/safe019_power.oepc.i"] = (1,1)
params["concurrency/pthread-wmm/safe019_rmo.oepc.i"] = (1,1)
params["concurrency/pthread-wmm/safe025_power.oepc.i"] = (1,1)
params["concurrency/pthread-wmm/safe025_power.opt.i"] = (1,1)
params["concurrency/pthread-wmm/safe027_power.oepc.i"] = (1,1)
params["concurrency/pthread-wmm/safe027_rmo.oepc.i"] = (1,1)
params["concurrency/pthread-wmm/safe027_rmo.opt.i"] = (1,1)
params["concurrency/pthread-wmm/thin000_power.oepc.i"] = (1,1)
params["concurrency/pthread-wmm/thin000_rmo.oepc.i"] = (1,1)
params["concurrency/pthread-wmm/thin000_rmo.opt.i"] = (1,1)
params["concurrency/pthread-wmm/thin001_power.oepc.i"] = (1,1)
params["concurrency/pthread-wmm/thin001_rmo.oepc.i"] = (1,1)
params["concurrency/pthread-wmm/thin001_rmo.opt.i"] = (1,1)
params["concurrency/pthread-wmm/thin002_power.oepc.i"] = (1,1)
params["concurrency/pthread-wmm/thin002_rmo.oepc.i"] = (1,1)
params["concurrency/pthread-wmm/thin002_rmo.opt.i"] = (1,1)
params["concurrency/pthread-wmm/mix000_power.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix000_power.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix000_pso.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix000_pso.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix000_rmo.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix000_rmo.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix000_tso.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix000_tso.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix001_power.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix001_power.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix001_pso.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix001_pso.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix001_rmo.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix001_rmo.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix001_tso.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix001_tso.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix002_power.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix002_power.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix002_pso.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix002_pso.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix002_rmo.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix002_rmo.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix002_tso.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix002_tso.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix003_power.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix003_power.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix003_pso.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix003_pso.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix003_rmo.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix003_rmo.opt.0.1.i"] = (1,2)
params["concurrency/pthread-wmm/mix003_rmo.opt.0.i"] = (1,2)
params["concurrency/pthread-wmm/mix003_rmo.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix003_tso.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix003_tso.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix004_power.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix004_power.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix004_pso.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix004_pso.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix004_rmo.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix004_rmo.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix004_tso.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix004_tso.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix005_power.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix005_power.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix005_pso.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix005_pso.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix005_rmo.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix005_rmo.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix005_tso.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix005_tso.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix006_power.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix006_power.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix006_pso.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix006_pso.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix006_rmo.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix006_rmo.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix006_tso.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix006_tso.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix007_power.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix007_power.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix007_pso.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix007_pso.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix007_rmo.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix007_rmo.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix007_tso.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix007_tso.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix008_power.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix008_power.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix008_pso.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix008_pso.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix008_rmo.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix008_rmo.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix008_tso.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix008_tso.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix009_power.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix009_power.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix009_pso.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix009_pso.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix009_rmo.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix009_rmo.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix009_tso.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix009_tso.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix010_power.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix010_power.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix010_pso.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix010_pso.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix010_rmo.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix010_rmo.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix010_tso.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix010_tso.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix011_power.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix011_power.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix011_pso.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix011_pso.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix011_rmo.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix011_rmo.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix011_tso.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix011_tso.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix012_power.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix012_power.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix012_pso.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix012_pso.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix012_rmo.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix012_rmo.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix012_tso.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix012_tso.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix013_power.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix013_power.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix013_pso.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix013_pso.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix013_rmo.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix013_rmo.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix013_tso.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix013_tso.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix014_power.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix014_power.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix014_pso.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix014_pso.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix014_rmo.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix014_rmo.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix014_tso.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix014_tso.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix015_power.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix015_power.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix015_pso.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix015_pso.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix015_rmo.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix015_rmo.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix015_tso.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix015_tso.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix016_power.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix016_power.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix016_pso.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix016_pso.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix016_rmo.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix016_rmo.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix016_tso.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix016_tso.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix017_power.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix017_power.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix017_pso.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix017_pso.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix017_rmo.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix017_rmo.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix017_tso.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix017_tso.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix018_power.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix018_power.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix018_pso.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix018_pso.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix018_rmo.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix018_rmo.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix018_tso.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix018_tso.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix019_power.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix019_power.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix019_pso.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix019_pso.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix019_rmo.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix019_rmo.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix019_tso.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix019_tso.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix020_power.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix020_power.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix020_pso.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix020_pso.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix020_rmo.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix020_rmo.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix020_tso.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix020_tso.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix021_power.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix021_power.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix021_pso.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix021_pso.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix021_rmo.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix021_rmo.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix021_tso.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix021_tso.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix022_power.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix022_power.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix022_pso.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix022_pso.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix022_rmo.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix022_rmo.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix022_tso.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix022_tso.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix023_power.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix023_power.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix023_pso.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix023_pso.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix023_rmo.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix023_rmo.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix023_tso.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix023_tso.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix024_power.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix024_power.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix024_pso.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix024_pso.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix024_rmo.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix024_rmo.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix024_tso.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix024_tso.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix025_power.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix025_power.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix025_pso.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix025_pso.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix025_rmo.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix025_rmo.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix025_tso.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix025_tso.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix026_power.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix026_power.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix026_pso.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix026_pso.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix026_rmo.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix026_rmo.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix026_tso.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix026_tso.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix027_power.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix027_power.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix027_pso.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix027_pso.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix027_rmo.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix027_rmo.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix027_tso.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix027_tso.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix028_power.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix028_power.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix028_pso.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix028_pso.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix028_rmo.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix028_rmo.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix028_tso.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix028_tso.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix029_power.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix029_power.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix029_pso.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix029_pso.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix029_rmo.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix029_rmo.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix029_tso.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix029_tso.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix030_power.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix030_power.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix030_pso.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix030_pso.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix030_rmo.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix030_rmo.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix030_tso.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix030_tso.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix031_power.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix031_power.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix031_pso.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix031_pso.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix031_rmo.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix031_rmo.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix031_tso.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix031_tso.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix032_power.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix032_power.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix032_pso.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix032_pso.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix032_rmo.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix032_rmo.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix032_tso.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix032_tso.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix033_power.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix033_power.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix033_pso.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix033_pso.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix033_rmo.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix033_rmo.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix033_tso.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix033_tso.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix034_power.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix034_power.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix034_pso.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix034_pso.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix034_rmo.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix034_rmo.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix034_tso.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix034_tso.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix035_power.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix035_power.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix035_pso.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix035_pso.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix035_rmo.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix035_rmo.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix035_tso.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix035_tso.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix036_power.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix036_power.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix036_pso.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix036_pso.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix036_rmo.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix036_rmo.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix036_tso.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix036_tso.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix037_power.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix037_power.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix037_pso.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix037_pso.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix037_rmo.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix037_rmo.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix037_tso.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix037_tso.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix038_power.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix038_power.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix038_pso.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix038_pso.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix038_rmo.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix038_rmo.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix038_tso.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix038_tso.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix039_power.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix039_power.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix039_pso.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix039_pso.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix039_rmo.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix039_rmo.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix039_tso.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix039_tso.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix040_power.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix040_power.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix040_pso.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix040_pso.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix040_rmo.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix040_rmo.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix040_tso.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix040_tso.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix041_power.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix041_power.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix041_pso.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix041_pso.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix041_rmo.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix041_rmo.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix041_tso.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix041_tso.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix042_power.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix042_power.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix042_pso.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix042_pso.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix042_rmo.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix042_rmo.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix042_tso.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix042_tso.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix043_power.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix043_power.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix043_pso.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix043_pso.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix043_rmo.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix043_rmo.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix043_tso.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix043_tso.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix044_power.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix044_power.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix044_pso.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix044_pso.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix044_rmo.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix044_rmo.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix044_tso.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix044_tso.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix045_power.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix045_power.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix045_pso.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix045_pso.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix045_rmo.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix045_rmo.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix045_tso.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix045_tso.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix046_power.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix046_power.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix046_pso.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix046_pso.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix046_rmo.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix046_rmo.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix046_tso.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix046_tso.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix047_power.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix047_power.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix047_pso.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix047_pso.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix047_rmo.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix047_rmo.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix047_tso.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix047_tso.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix048_power.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix048_power.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix048_pso.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix048_pso.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix048_rmo.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix048_rmo.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix048_tso.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix048_tso.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix049_power.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix049_power.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix049_pso.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix049_pso.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix049_rmo.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix049_rmo.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix049_tso.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix049_tso.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix050_power.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix050_power.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix050_pso.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix050_pso.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix050_rmo.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix050_rmo.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix050_tso.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix050_tso.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix051_power.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix051_power.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix051_pso.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix051_pso.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix051_rmo.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix051_rmo.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix051_tso.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix051_tso.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix052_power.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix052_power.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix052_pso.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix052_pso.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix052_rmo.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix052_rmo.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix052_tso.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix052_tso.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix053_power.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix053_power.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix053_pso.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix053_pso.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix053_rmo.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix053_rmo.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix053_tso.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix053_tso.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix054_power.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix054_power.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix054_pso.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix054_pso.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix054_rmo.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix054_rmo.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix054_tso.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix054_tso.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix055_power.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix055_power.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix055_pso.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix055_pso.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix055_rmo.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix055_rmo.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix055_tso.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix055_tso.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix056_power.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix056_power.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix056_pso.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix056_pso.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix056_rmo.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix056_rmo.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix056_tso.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix056_tso.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix057_power.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix057_power.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix057_pso.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix057_pso.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix057_rmo.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix057_rmo.opt.i"] = (1,2)
params["concurrency/pthread-wmm/mix057_tso.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/mix057_tso.opt.i"] = (1,2)
params["concurrency/pthread-wmm/podwr000_power.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/podwr000_power.opt.i"] = (1,2)
params["concurrency/pthread-wmm/podwr000_pso.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/podwr000_pso.opt.i"] = (1,2)
params["concurrency/pthread-wmm/podwr000_rmo.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/podwr000_rmo.opt.i"] = (1,2)
params["concurrency/pthread-wmm/podwr000_tso.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/podwr000_tso.opt.i"] = (1,2)
params["concurrency/pthread-wmm/podwr001_power.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/podwr001_power.opt.i"] = (1,2)
params["concurrency/pthread-wmm/podwr001_pso.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/podwr001_pso.opt.i"] = (1,2)
params["concurrency/pthread-wmm/podwr001_rmo.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/podwr001_rmo.opt.i"] = (1,2)
params["concurrency/pthread-wmm/podwr001_tso.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/podwr001_tso.opt.i"] = (1,2)
params["concurrency/pthread-wmm/rfi000_power.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/rfi000_power.opt.i"] = (1,2)
params["concurrency/pthread-wmm/rfi000_pso.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/rfi000_pso.opt.i"] = (1,2)
params["concurrency/pthread-wmm/rfi000_rmo.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/rfi000_rmo.opt.i"] = (1,2)
params["concurrency/pthread-wmm/rfi001_power.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/rfi001_power.opt.i"] = (1,2)
params["concurrency/pthread-wmm/rfi001_pso.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/rfi001_pso.opt.i"] = (1,2)
params["concurrency/pthread-wmm/rfi001_rmo.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/rfi001_rmo.opt.i"] = (1,2)
params["concurrency/pthread-wmm/rfi001_tso.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/rfi001_tso.opt.i"] = (1,2)
params["concurrency/pthread-wmm/rfi003_power.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/rfi003_power.opt.i"] = (1,2)
params["concurrency/pthread-wmm/rfi003_pso.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/rfi003_pso.opt.i"] = (1,2)
params["concurrency/pthread-wmm/rfi003_rmo.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/rfi003_rmo.opt.i"] = (1,2)
params["concurrency/pthread-wmm/rfi004_power.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/rfi004_power.opt.i"] = (1,2)
params["concurrency/pthread-wmm/rfi004_pso.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/rfi004_pso.opt.i"] = (1,2)
params["concurrency/pthread-wmm/rfi004_rmo.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/rfi004_rmo.opt.i"] = (1,2)
params["concurrency/pthread-wmm/rfi004_tso.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/rfi004_tso.opt.i"] = (1,2)
params["concurrency/pthread-wmm/rfi006_pso.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/rfi006_pso.opt.i"] = (1,2)
params["concurrency/pthread-wmm/rfi006_tso.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/rfi006_tso.opt.i"] = (1,2)
params["concurrency/pthread-wmm/rfi007_power.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/rfi007_power.opt.i"] = (1,2)
params["concurrency/pthread-wmm/rfi007_pso.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/rfi007_pso.opt.i"] = (1,2)
params["concurrency/pthread-wmm/rfi007_rmo.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/rfi007_rmo.opt.i"] = (1,2)
params["concurrency/pthread-wmm/rfi007_tso.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/rfi007_tso.opt.i"] = (1,2)
params["concurrency/pthread-wmm/rfi008_power.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/rfi008_power.opt.i"] = (1,2)
params["concurrency/pthread-wmm/rfi008_pso.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/rfi008_pso.opt.i"] = (1,2)
params["concurrency/pthread-wmm/rfi008_rmo.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/rfi008_rmo.opt.i"] = (1,2)
params["concurrency/pthread-wmm/rfi008_tso.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/rfi008_tso.opt.i"] = (1,2)
params["concurrency/pthread-wmm/rfi009_power.opt.i"] = (1,2)
params["concurrency/pthread-wmm/rfi009_pso.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/rfi009_pso.opt.i"] = (1,2)
params["concurrency/pthread-wmm/rfi009_rmo.opt.i"] = (1,2)
params["concurrency/pthread-wmm/rfi009_tso.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/rfi009_tso.opt.i"] = (1,2)
params["concurrency/pthread-wmm/rfi010_power.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/rfi010_power.opt.i"] = (1,2)
params["concurrency/pthread-wmm/rfi010_pso.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/rfi010_pso.opt.i"] = (1,2)
params["concurrency/pthread-wmm/rfi010_rmo.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/rfi010_rmo.opt.i"] = (1,2)
params["concurrency/pthread-wmm/rfi010_tso.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/rfi010_tso.opt.i"] = (1,2)
params["concurrency/pthread-wmm/safe000_power.opt.i"] = (1,2)
params["concurrency/pthread-wmm/safe001_power.opt.i"] = (1,2)
params["concurrency/pthread-wmm/safe001_pso.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/safe001_pso.opt.i"] = (1,2)
params["concurrency/pthread-wmm/safe001_rmo.opt.i"] = (1,2)
params["concurrency/pthread-wmm/safe002_power.opt.i"] = (1,2)
params["concurrency/pthread-wmm/safe002_pso.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/safe002_pso.opt.i"] = (1,2)
params["concurrency/pthread-wmm/safe002_rmo.opt.i"] = (1,2)
params["concurrency/pthread-wmm/safe003_power.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/safe003_power.opt.i"] = (1,2)
params["concurrency/pthread-wmm/safe003_pso.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/safe003_pso.opt.i"] = (1,2)
params["concurrency/pthread-wmm/safe003_rmo.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/safe003_rmo.opt.i"] = (1,2)
params["concurrency/pthread-wmm/safe004_power.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/safe004_power.opt.i"] = (1,2)
params["concurrency/pthread-wmm/safe004_pso.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/safe004_pso.opt.i"] = (1,2)
params["concurrency/pthread-wmm/safe004_rmo.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/safe004_rmo.opt.i"] = (1,2)
params["concurrency/pthread-wmm/safe005_power.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/safe005_power.opt.i"] = (1,2)
params["concurrency/pthread-wmm/safe005_pso.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/safe005_pso.opt.i"] = (1,2)
params["concurrency/pthread-wmm/safe005_rmo.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/safe005_rmo.opt.i"] = (1,2)
params["concurrency/pthread-wmm/safe006_power.opt.i"] = (1,2)
params["concurrency/pthread-wmm/safe007_power.opt.i"] = (1,2)
params["concurrency/pthread-wmm/safe008_power.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/safe008_power.opt.i"] = (1,2)
params["concurrency/pthread-wmm/safe008_pso.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/safe008_pso.opt.i"] = (1,2)
params["concurrency/pthread-wmm/safe008_rmo.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/safe008_rmo.opt.i"] = (1,2)
params["concurrency/pthread-wmm/safe009_power.opt.i"] = (1,2)
params["concurrency/pthread-wmm/safe009_rmo.opt.i"] = (1,2)
params["concurrency/pthread-wmm/safe010_power.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/safe010_power.opt.i"] = (1,2)
params["concurrency/pthread-wmm/safe010_pso.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/safe010_pso.opt.i"] = (1,2)
params["concurrency/pthread-wmm/safe010_rmo.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/safe010_rmo.opt.i"] = (1,2)
params["concurrency/pthread-wmm/safe011_power.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/safe011_power.opt.i"] = (1,2)
params["concurrency/pthread-wmm/safe011_pso.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/safe011_pso.opt.i"] = (1,2)
params["concurrency/pthread-wmm/safe011_rmo.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/safe011_rmo.opt.i"] = (1,2)
params["concurrency/pthread-wmm/safe012_power.opt.i"] = (1,2)
params["concurrency/pthread-wmm/safe012_pso.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/safe012_pso.opt.i"] = (1,2)
params["concurrency/pthread-wmm/safe012_rmo.opt.i"] = (1,2)
params["concurrency/pthread-wmm/safe013_power.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/safe013_power.opt.i"] = (1,2)
params["concurrency/pthread-wmm/safe013_pso.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/safe013_pso.opt.i"] = (1,2)
params["concurrency/pthread-wmm/safe013_rmo.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/safe013_rmo.opt.i"] = (1,2)
params["concurrency/pthread-wmm/safe014_rmo.opt.i"] = (1,2)
params["concurrency/pthread-wmm/safe015_power.opt.i"] = (1,2)
params["concurrency/pthread-wmm/safe015_rmo.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/safe015_rmo.opt.i"] = (1,2)
params["concurrency/pthread-wmm/safe016_power.opt.i"] = (1,2)
params["concurrency/pthread-wmm/safe016_rmo.opt.i"] = (1,2)
params["concurrency/pthread-wmm/safe017_power.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/safe017_power.opt.i"] = (1,2)
params["concurrency/pthread-wmm/safe017_pso.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/safe017_pso.opt.i"] = (1,2)
params["concurrency/pthread-wmm/safe017_rmo.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/safe017_rmo.opt.i"] = (1,2)
params["concurrency/pthread-wmm/safe018_power.opt.i"] = (1,2)
params["concurrency/pthread-wmm/safe018_rmo.opt.i"] = (1,2)
params["concurrency/pthread-wmm/safe019_power.opt.i"] = (1,2)
params["concurrency/pthread-wmm/safe019_rmo.opt.i"] = (1,2)
params["concurrency/pthread-wmm/safe020_power.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/safe020_power.opt.i"] = (1,2)
params["concurrency/pthread-wmm/safe020_rmo.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/safe020_rmo.opt.i"] = (1,2)
params["concurrency/pthread-wmm/safe021_power.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/safe021_power.opt.i"] = (1,2)
params["concurrency/pthread-wmm/safe021_pso.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/safe021_pso.opt.i"] = (1,2)
params["concurrency/pthread-wmm/safe021_rmo.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/safe021_rmo.opt.i"] = (1,2)
params["concurrency/pthread-wmm/safe022_power.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/safe022_power.opt.i"] = (1,2)
params["concurrency/pthread-wmm/safe022_pso.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/safe022_pso.opt.i"] = (1,2)
params["concurrency/pthread-wmm/safe022_rmo.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/safe022_rmo.opt.i"] = (1,2)
params["concurrency/pthread-wmm/safe023_power.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/safe023_power.opt.i"] = (1,2)
params["concurrency/pthread-wmm/safe023_pso.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/safe023_pso.opt.i"] = (1,2)
params["concurrency/pthread-wmm/safe023_rmo.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/safe023_rmo.opt.i"] = (1,2)
params["concurrency/pthread-wmm/safe024_power.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/safe024_power.opt.i"] = (1,2)
params["concurrency/pthread-wmm/safe024_pso.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/safe024_pso.opt.i"] = (1,2)
params["concurrency/pthread-wmm/safe024_rmo.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/safe024_rmo.opt.i"] = (1,2)
params["concurrency/pthread-wmm/safe025_rmo.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/safe025_rmo.opt.i"] = (1,2)
params["concurrency/pthread-wmm/safe026_power.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/safe026_power.opt.i"] = (1,2)
params["concurrency/pthread-wmm/safe026_pso.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/safe026_pso.opt.i"] = (1,2)
params["concurrency/pthread-wmm/safe026_rmo.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/safe026_rmo.opt.i"] = (1,2)
params["concurrency/pthread-wmm/safe027_power.opt.i"] = (1,2)
params["concurrency/pthread-wmm/safe028_power.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/safe028_power.opt.i"] = (1,2)
params["concurrency/pthread-wmm/safe028_rmo.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/safe028_rmo.opt.i"] = (1,2)
params["concurrency/pthread-wmm/safe029_power.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/safe029_power.opt.i"] = (1,2)
params["concurrency/pthread-wmm/safe029_pso.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/safe029_pso.opt.i"] = (1,2)
params["concurrency/pthread-wmm/safe029_rmo.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/safe029_rmo.opt.i"] = (1,2)
params["concurrency/pthread-wmm/safe030_power.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/safe030_power.opt.i"] = (1,2)
params["concurrency/pthread-wmm/safe030_pso.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/safe030_pso.opt.i"] = (1,2)
params["concurrency/pthread-wmm/safe030_rmo.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/safe030_rmo.opt.i"] = (1,2)
params["concurrency/pthread-wmm/safe031_power.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/safe031_power.opt.i"] = (1,2)
params["concurrency/pthread-wmm/safe031_pso.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/safe031_pso.opt.i"] = (1,2)
params["concurrency/pthread-wmm/safe031_rmo.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/safe031_rmo.opt.i"] = (1,2)
params["concurrency/pthread-wmm/safe032_power.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/safe032_power.opt.i"] = (1,2)
params["concurrency/pthread-wmm/safe032_pso.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/safe032_pso.opt.i"] = (1,2)
params["concurrency/pthread-wmm/safe032_rmo.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/safe032_rmo.opt.i"] = (1,2)
params["concurrency/pthread-wmm/safe033_power.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/safe033_power.opt.i"] = (1,2)
params["concurrency/pthread-wmm/safe033_pso.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/safe033_pso.opt.i"] = (1,2)
params["concurrency/pthread-wmm/safe033_rmo.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/safe033_rmo.opt.i"] = (1,2)
params["concurrency/pthread-wmm/safe034_power.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/safe034_power.opt.i"] = (1,2)
params["concurrency/pthread-wmm/safe034_pso.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/safe034_pso.opt.i"] = (1,2)
params["concurrency/pthread-wmm/safe034_rmo.oepc.i"] = (1,2)
params["concurrency/pthread-wmm/safe034_rmo.opt.i"] = (1,2)
params["concurrency/pthread-wmm/thin000_power.opt.i"] = (1,2)
params["concurrency/pthread-wmm/thin001_power.opt.i"] = (1,2)
params["concurrency/pthread-wmm/thin002_power.opt.i"] = (1,2)

# options
command = {}
command['cbmc'] = 'backends/cbmc-5.4 --32'
command['cbmc-svcomp2020'] = 'backends/cbmc-5.12 --32'
command['esbmc'] = 'backends/esbmc --32 '


command['cpachecker'] = 'backends/CPAchecker-1.9-unix/scripts/cpa.sh -32 -svcomp20 -timelimit 1200s -stats'
command['yogar'] = 'backends/yogar-cbmc/yogar-cbmc  --no-unwinding-assertions --32'
command['divine'] = 'backends/divine/divine verify'
command['mu-cseq'] = './mu-cseq-test.sh'
command['ul-cseq'] = './ul-cseq-test.sh'
command['lr-cseq'] = './lr-cseq-test.sh'

ok = {}
ok['cbmc'] = 'VERIFICATION SUCCESSFUL'
ok['cbmc-svcomp2020'] = 'VERIFICATION SUCCESSFUL'
ok['esbmc'] = 'VERIFICATION SUCCESSFUL'
ok['cpachecker'] = 'Verification result: TRUE.'
ok['yogar'] = 'VERIFICATION SUCCESSFUL'
ok['divine'] = 'error found: no'
ok['mu-cseq'] = ', TRUE, '
ok['ul-cseq'] = ', TRUE, '
ok['lr-cseq'] = 'TRUE'

ko = {}
ko['esbmc'] = 'VERIFICATION FAILED'
ko['cbmc'] = 'VERIFICATION FAILED'
ko['cbmc-svcomp2020'] = 'VERIFICATION FAILED'
ko['cpachecker'] = 'Verification result: FALSE.' #ko['smack'] = 'Error BP5001: This assertion might not hold.\n'
ko['yogar'] = 'Violated property:'
ko['divine'] = 'FAULT: verifier error called'
ko['mu-cseq'] = ', FALSE, '
ko['ul-cseq'] = ', FALSE, '
ko['lr-cseq'] = 'FALSE'

import shlex, signal, subprocess, threading, time, resource, multiprocessing
from threading import Thread, Lock
from multiprocessing import Pool
import Queue
import core.utils

lock = threading.Lock()   # for mutual exclusion on log entries


def indent(s,char='|'):
	t = ''
	for l in s.splitlines(): t += '   %s%s'%(char,l)+'\n'
	return t

import logging


''' Checks whether in the .yml file the test case is marked as safe or unsafe
'''
def falseortrue(filename):
	with open(filename, 'r') as f:
		lines = f.read().splitlines()

		for l in lines:
			if  "false-unreach-call" in l: return False  # may have multiple properties

		return True


'''
'''
def feed2(file):
	global backend

	starttime = time.time()

	k=file[:file.find(' ')]
	file = file[file.find(' '):]
	file = file.lstrip()

	# verify
	#
	(unwind,rounds) = params[file]

	#opt = opts[backend] if backend in opts else ''
	#cmd = 'ulimit -Sv %s && /usr/bin/timeout --signal=SIGTERM %s ./cseq.py --show-backend-output --verbose --input %s --nondet-condvar-wakeups --rounds %s --unwind %s --backend %s %s' %(int(memory)*1024*1024,timeout,file,rounds,unwind,backend,opt)
	if backend != 'lr-cseq':
		cmd = 'ulimit -Sv %s && /usr/bin/timeout --signal=SIGKILL %s %s %s' %(int(memory)*1024*1024,timeout,command[backend],file)
	else:
		cmd = 'ulimit -Sv %s && /usr/bin/timeout --signal=SIGKILL %s %s %s' %(int(memory)*1024*1024,timeout,command[backend],file.replace('.i','.c'))

	if backend == 'cbmc': cmd += ' --unwind %s ' % (unwind+1)
	if backend == 'cbmc-svcomp2020': cmd += ' --unwind %s ' % (unwind+1)
	if backend == 'esbmc': cmd += ' --unwind %s --context-bound %s' % (unwind+1,rounds+1)
	if backend == 'lr-cseq': cmd += ' --unwind %s ' % (unwind)

	cmd = '%s 2>&1' % cmd

	p = core.utils.CommandPid(cmd)
	p.spawn()   # store stdout, stderr, process' return value
	out,err,cod,mem = p.wait(0)


	check = ''

	#if 'UNSAFE' in out and not falseortrue(file.replace('.i','.yml')): check = 'PASS'
	#elif 'SAFE' in out and not falseortrue(file.replace('.i','.yml')): check = 'FAIL'
	#elif 'SAFE' in out and falseortrue(file.replace('.i','.yml')): check = 'PASS'
	#elif 'UNSAFE' in out and falseortrue(file.replace('.i','.yml')): check = 'FAIL'
	#else: check = 'UNKN'
	if ko[backend] in out and not falseortrue(file.replace('.i','.yml')): check = 'PASS'
	elif ok[backend] in out and not falseortrue(file.replace('.i','.yml')): check = 'FAIL'
	elif ok[backend] in out and falseortrue(file.replace('.i','.yml')): check = 'PASS'
	elif ko[backend] in out and falseortrue(file.replace('.i','.yml')): check = 'FAIL'
	else: check = 'UNKN'

	log = ''
	log += cmd+'\n'
	log += indent(out)
	#log += indent(err)

	if check == 'UNKN':
		out = out + ' '+file

	# UNKN+code=1 -> insufficient memory.
	# code=124 -> insufficient time.
	# code=10  -> CSeq error
	details = str(cod).zfill(3)

	check = "%s (%s)" % (check, details)

	#log += "stop, %s, " % (check + ', '+ out + '\n')
	log += "stop, %s, %s, %0.2fs, %0.2fMB\n" % (check,file,time.time()-starttime,mem)

	return log


def listfiles(path='./'):
	return [y for x in os.walk(path) for y in glob(os.path.join(x[0], '*.i'))]


def usage(cmd, errormsg):
	print "CSeq Tester"
	print ""
	print " Usage:"
	print "   -h, --help                    display this help screen"
	print ""
	print "   -i<path>, --input=<path>      path to a single .i file"
	print "   -p<path>, --path=<path>       path to recursively scan for .i files"
	print "\n"
	print "  Notes:"
	print "       (1) for quickly checking that something did not break the tool: use --quick"
	print "       (2) for a full round with real bounds: use no extra parameters"
	print "       (3) for a full round with real bounds and witness checking: use --witness-check"
	print ""
	print '\n' + errormsg + '\n'
	sys.exit(1)


def main(args):
	global backend,memory,timeout,cores

	cmd = args[0]

	try:
		opts, args = getopt.getopt(sys.argv[1:], "hi:p:b:t:m:c:", ["help", "input=", "path=", "backend=", "time=", "memory=", "cores="])
	except getopt.GetoptError, err:
		print "error"
		usage(cmd, 'error: ' +str(err))

	inputfile = inputpath = ''

	for o, a in opts:
		if o in ("-h", "--help"): usage(cmd, "")
		elif o in ("-i", "--input"): inputfile = a
		elif o in ("-p", "--path"): inputpath = a
		elif o in ("-b", "--backend"): backend = a
		elif o in ("-t", "--time"): timeout = a
		elif o in ("-m", "--memory"): memory = a
		elif o in ("-c", "--cores"): cores = int(a)
		else: assert False, "unhandled option"

	if inputfile == inputpath == '':
		print 'error: source file or path not specified'
		sys.exit(1)

	# List the programs to analyse..
	sortedfiles = None

	if inputfile != '':
		sortedfiles = []
		sortedfiles.append(inputfile)
	elif inputpath != '':
		sortedfiles = sorted(listfiles(inputpath))

	# ..filter out programs without a bug..
	filteredfiles = []
	filteredcount = 0
	filtered2sorted = {}  # map indexes from initial list of files to filtered files

	for i,f in enumerate(sortedfiles):
		if falseortrue(f.replace('.i','.yml')) == False:
			filteredfiles.append(str(i+1)+' '+f)  # embed the index
			filtered2sorted[filteredcount+1] = i+1
			filteredcount += 1

	# ..and spawn a separate analyser for each program.
	pool = Pool(processes=cores,maxtasksperchild=1)
	k=0

	try:
		for i in pool.imap(feed2,filteredfiles):
			k+=1

			with lock:
				print(indent(i,str(filtered2sorted[k]).zfill(4) + '> '))

	except (KeyboardInterrupt, SystemExit) as e:
		sys.exit(0)
	except Exception as e:
		print("EXCEPTION : %s" % (str(e)))
		#traceback.print_exc(file=sys.stdout)


if __name__ == "__main__":
	main(sys.argv[0:])


