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
    data = SloppyTree(dict(args))

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
    # glob the input files.
    ###
    if 'all' in args.inputs:
        data.inputs = glob.glob(programs[args.exe].inputfiles) 
    else:
        x = []
        data.inputs = x.extend(glob.glob(inp) for inp in args.inputs)
    
    if not args.inputs:
        print("No input files found.")
        sys.exit(os.EX_DATAERR)
        
    data.inputs = args.inputs
    data.email = args.mailuser

    return data


@trap
def autoslurm_main(args:argparse.Namespace) -> int:
    """
    Write a SLURM job file, and optionally submit it.
    """
    data = fixup_args(args)

    results = []
    # Iterate over passed inputs
    for inp in data.inputs:

        ## Job Name
        data.jobname = ( args.jobname 
            if args.jobname else 
            ".".join(inp.split('.')[:-1]) )

        ## CPUs and memory are set here.
        data.mpisockets = 2 if cputotal > 26 else 1
        data.ompthreads = cputotal // mpisockets
        data.mem = min(args.mem, cluster_data.partition.ram)
        
        # Generate the SLURM script. To make changes, edit the
        # scripts.py file that is a part of this project.
        with open(f"{data.jobname}.slurm", 'w+') as f:
            s = slurm[data.exe](data)
            # Writes the SLURM string to the file
            f.write(s)

        # Prints out the SLURM file to terminal if --dryrun was specified
        if args.dryrun:
            print(s)

        # Runs the calculation otherwise
        else:
             results.append(dorunrun(f"sbatch {jobname}.slurm", 
                return_datatype=int))

    # Return appropriate exit status.
    return os.EX_OK if not sum(results) else max(results)


if __name__ == "__main__":

    from autoslurmhelp import helptext

    parser = argparse.ArgumentParser(description=helptext.description)
    parser.add_argument('inputs', nargs='+', type=list, help=helptext.inputs)

    parser.add_argument('-mt', '--mailtype', type=str, default="NONE", 
        choices=('NONE', 'BEGIN', 'END', 'FAIL', 'REQUEUE', 'ALL'), 
        help=helptext.mailtype)

    parser.add_argument('-mu', '--mailuser', type=str, default=mynetid, 
        help=helptext.mailuser)

    parser.add_argument('-j', '--jobname', default=None, type=str,
        help=helptext.jobname)

    parser.add_argument('-c', '--cputotal', default=24, type=int,
        choices=(range(50)), help=helptext.cputotal)

    parser.add_argument('-m', '--mem', default=380, type=int, help=helptext.mem)

    parser.add_argument('-q', '--partition', default='basic', type=str,
        choices=(cluster_data.partitions.keys()), help=helptext.partition)

    parser.add_argument('-x', '--exe', default='qchem', type=str,
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
    verbose = myargs.verbose

    try:
        outfile = sys.stdout if not myargs.output else open(myargs.output, 'w')
        with contextlib.redirect_stdout(outfile):
            sys.exit(globals()[f"{os.path.basename(__file__)[:-3]}_main"](myargs))

    except Exception as e:
        print(f"Escaped or re-raised exception: {e}")

