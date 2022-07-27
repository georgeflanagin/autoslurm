# -*- coding: utf-8 -*-
import typing
from   typing import *

min_py = (3, 8)

###
# Standard imports, starting with os and sys
###
import os
import sys
if sys.version_info < min_py:
    print(f"This program requires Python {min_py[0]}.{min_py[1]}, or higher.")
    sys.exit(os.EX_SOFTWARE)

__author__ = ['Dominic A. Sirianni']
__credits__ = ['Dominic A. Sirianni','Travis E. Greene']
__copyright__ = '(c) 2022 The Parish Lab'
__license__ = "BSD-3-Clause"
__date__ = "2022-07-06"
__email__ = "sirianni.dom@gmail.com"

###
# Other standard distro imports
###
import argparse
import contextlib
import getpass
mynetid = getpass.getuser()
import glob

###
# From hpclib
###
import linuxutils
from   sloppytree import SloppyTree
import slurmutils
from   urdecorators import trap

###
# imports and objects that are a part of this project
###
from scripts import slurm
from programs import programs

verbose = False


cluster_data = slurmutils.parse_sinfo()
all_partitions = set(( k for k in cluster_data.keys() ))
condos = set(('bukach', 'diaz', 'erickson', 'johnson', 
                'parish', 'yang1', 'yang2', 'yangnolin'))
community_partitions_plenum = all_partitions - condos

@trap
def fixup_args(args:argparse.Namespace) -> SloppyTree:
    """
    Do the little bit of proofreading that is required after
    argparse reads the command line.
    """
    global cluster_data
    global verbose
    global mynetid

    data = SloppyTree(vars(args))
    data.user = mynetid

    ###
    # Ensure the version of the program to be run makes some sense.
    # If no version is given, assume that the latest version is
    # the one to use, and assume the largest version number is
    # the latest one.
    ###
    if not data.version:
        data.version = max(programs[myargs.exe].versions)
    elif data.version not in programs[data.exe].versions:
        print(f"{data.exe} does not have a version {data.version}")
        sys.exit(os.EX_CONFIG)
    else:
        # data.version does not need to be changed.
        pass

    ###
    # glob the input files. Note the two different cases where
    # we check if there are any file. The first time, we see
    # if the user has *supplied* any, and the second time
    # we see if this program has *found* any.
    ###
    data.inputs = []
    my_exe = programs[args.exe]

    if not args.inputs and not os.getenv('AUTOSLURM_DEFAULT_DIR'):
        print("No target locations given.")
        sys.exit(os.EX_NOINPUT)
    else:
        args.inputs = [os.getenv('AUTOSLURM_DEFAULT_DIR')]

    data.defaultdir = os.getenv('AUTOSLURM_DEFAULT_DIR')
        
    for input_spec in args.inputs:
        if os.path.isdir(input_spec):
            data.inputs.extend(glob.glob(os.path.join(input_spec, my_exe.inputfiles)))
        elif os.path.isfile(input_spec):
            data.inputs.extend([input_spec])
        else:
            data.inputs.extend(glob.glob(input_spec)) 

    if data.inputs:
        verbose and print(f"{data.inputs=}")
    else:
        print("No input files found.")
        sys.exit(os.EX_NOINPUT)
        
    data.email = args.mailuser
    data.program = my_exe.exe[data.version]

    return data


@trap
def autoslurm_main(args:argparse.Namespace) -> int:
    """
    Write a SLURM job file, and optionally submit it.
    """
    global verbose
    data = fixup_args(args)
    verbose and print(f"{data=}")

    results = []
    # Iterate over passed inputs
    for inp in data.inputs:
        data.inp = inp
        verbose and print(f"{inp=}")

        ## Job Name
        data.jobname = ( args.jobname 
            if args.jobname else 
            ".".join(os.path.basename(inp).split('.')[:-1]) )

        ## CPUs and memory are set here.
        data.mpisockets = 2 if args.cputotal > 26 else 1
        data.ompthreads = args.cputotal // data.mpisockets
        verbose and print(f"{cluster_data=}")
        data.mem = min(args.mem, cluster_data[args.partition].ram)
        
        # Generate the SLURM script. To make changes, edit the
        # scripts.py file that is a part of this project.
        s = slurm[data.exe](data)
        try:
            with open(f"{data.defaultdir}/{data.jobname}.slurm", 'w+') as f:
                # Writes the SLURM string to the file
                f.write(s)
        except PermissionError as e:
            print(f"""
                Cannot open {data.defaultdir}/{data.jobname}.slurm for writing. 
                You will have to cut and paste from the screen.""")
            args.dryrun = True

        # Prints out the SLURM file to terminal if --dryrun was specified
        if args.dryrun:
            print(f"{s}")

        # Runs the calculation otherwise
        else:
             results.append(dorunrun(f"sbatch {jobname}.slurm", 
                return_datatype=int))

    # Return appropriate exit status.
    return os.EX_OK if not sum(results) else max(results)


if __name__ == "__main__":

    from autoslurmhelp import helptext

    parser = argparse.ArgumentParser(description=helptext.description)
    parser.add_argument('inputs', nargs='*', help=helptext.inputs)

    parser.add_argument('-mt', '--mailtype', type=str, default="NONE", 
        choices=('NONE', 'BEGIN', 'END', 'FAIL', 'REQUEUE', 'ALL'), 
        help=helptext.mailtype)

    parser.add_argument('-mu', '--mailuser', type=str, 
        default=f"{mynetid}@richmond.edu", 
        help=helptext.mailuser)

    parser.add_argument('-j', '--jobname', default="", type=str,
        help=helptext.jobname)

    parser.add_argument('-c', '--cputotal', default=24, type=int,
        choices=(range(50)), help=helptext.cputotal)

    parser.add_argument('-m', '--mem', default=380, type=int, help=helptext.mem)

    parser.add_argument('-q', '--partition', default='basic', type=str,
        choices=(cluster_data.keys()), help=helptext.partition)

    parser.add_argument('-x', '--exe', default='date', type=str,
        choices = slurm.keys(), help=helptext.exe)

    parser.add_argument('-v', '--version', default='', type=str, help=helptext.version)

    parser.add_argument('--dryrun', action='store_true', help=helptext.dryrun)

    parser.add_argument('-o', '--output', type=str, default="")

    parser.add_argument('--verbose', action='store_true',
        help="Be chatty about what is taking place")

    ######################################################################
    # Temporarily Removed Arguments
    # parser.add_argument('-t', '--ompthreads', default=12, 
    #      help="Number of threads for OpenMP parallelization")
    # parser.add_argument('-s', '--mpisockets', default=2, 
    #     help="Number of sockets for MPI parallelization")
    ######################################################################

    myargs = parser.parse_args()
    linuxutils.dump_cmdline(myargs)
    verbose = myargs.verbose

    try:
        outfile = sys.stdout if not myargs.output else open(myargs.output, 'w')
        with contextlib.redirect_stdout(outfile):
            sys.exit(globals()[f"{os.path.basename(__file__)[:-3]}_main"](myargs))

    except Exception as e:
        print(f"Escaped or re-raised exception: {e}")

