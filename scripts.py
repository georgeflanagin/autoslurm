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

###
# From hpclib
###
from   sloppytree import SloppyTree

###
# imports and objects that are a part of this project
###
verbose = False

__author__ = 'George Flanagin'
__copyright__ = 'Copyright 2022'
__credits__ = 'dsiriann@richmond.edu'
__version__ = 0.1
__maintainer__ = 'George Flanagin'
__email__ = ['gflanagi@richmond.edu']
__status__ = 'in progress'
__license__ = 'MIT'


slurm = SloppyTree()

###################################### QCHEM ##########################

slurm.qchem = lambda data : f"""#!/bin/bash -e

#SBATCH  --account={data.user}$
#SBATCH  --mail-type={data.mailtype}
#SBATCH  --mail-user={data.email}
#SBATCH  --job-name={data.jobname}
#SBATCH  --cpus-per-task={data.cputotal}
#SBATCH  --output {data.jobname}.tomb
#SBATCH  -e {data.jobname}.tomb.err
#SBATCH  --mem={data.mem*1000}M
#SBATCH  --tasks=1
#SBATCH  --partition={data.partition}

# Generates a filename of "random" digits to avoid overwriting/removing data
# Without this convention, this script would remove all files in a user's qchemScratch,
# canceling/ruining random jobs running on the same node.
scratchFolder="$(date +%N)"

# Prints the scratch folder name
echo "Scratch Folder: ${{scratchFolder}}"

# This function runs as soon as the SLURM job terminates.
# It's purpose is to make sure no files are left on the nodes and that your
# calculation data goes back to your own directory.
function cleanup {{
	
	# Moves the final data back to the current working directory where the script was run
	cp /localscratch/{data.user}/qchemScratch/${{scratchFolder}}/{data.jobname}.in {os.getcwd()}
	cp /localscratch/{data.user}/qchemScratch/${{scratchFolder}}/{data.jobname}.out {os.getcwd()}
	cp /localscratch/{data.user}/qchemScratch/${{scratchFolder}}/{data.jobname}.fchk {os.getcwd()}

	# Prints out what directory is being removed.
	echo "Removing /localscratch/{data.user}/qchemScratch/${{scratchFolder}}"
	rm -rf "/localscratch/{data.user}/qchemScratch/${{scratchFolder}}"
}}

# This creates an exit trap that runs the cleanup function on exit
trap cleanup EXIT

cd $SLURM_SUBMIT_DIR
echo "I ran on: $SLURM_NODELIST"
echo "Starting at `date`"

NAME={data.jobname}

# Get rid of all the random crap in your path, you don't want it here
export DATADIR={os.getcwd()}
module purge

# Make sure envvars are sourced properly
source /usr/local/sw/qchem/qchem{data.version}/qcenv.sh

# Exports the QCSCRATCH variable that Q-Chem will use as it's scratch directory
export QCSCRATCH="/localscratch/{data.user}/qchemScratch/${{scratchFolder}}"

# Creates (and does nothing if it already exists) the QCSCRATCH directory
mkdir -p $QCSCRATCH

# Copies the input file to that local scratch directory 
cp {os.getcwd()}/{data.jobname}.in $QCSCRATCH

# Changes directory to that local scratch directory in order to run Q-Chem
cd $QCSCRATCH

# Executes the script using these specifications
/usr/bin/time -v qchem -slurm -np {data.mpisockets} -nt {data.ompthreads} {data.jobname}.in {data.jobname}.out

#Record keeping
echo "Finished at `date`"
"""

################################### GAUSSIAN ##########################

slurm.gaussian = lambda data : f"""#!/bin/bash -e

### Primary SBATCH directives.

#SBATCH  --account={data.user}
#SBATCH  --mail-type={data.mailtype}
#SBATCH  --mail-user={data.email}
#SBATCH  --job-name={data.jobname}
#SBATCH  --cpus-per-task={data.cputotal}
#SBATCH  --output {data.jobname}.tomb
#SBATCH  -e {data.jobname}.tomb.err
#SBATCH  --mem={data.mem*1000}M
#SBATCH  --tasks=1
#SBATCH  --partition={data.partition}

#### Set the scratch folder, and the cleanup operation. ####

scratchFolder="$(date +%N)"
echo "Scratch Folder: ${{scratchFolder}}"
function cleanup {{
	
    cp /localscratch/{data.user}/gaussScratch/${{scratchFolder}}/{data.jobname}.in {os.getcwd()}
    cp /localscratch/{data.user}/gaussScratch/${{scratchFolder}}/{data.jobname}.out {os.getcwd()}
    cp /localscratch/{data.user}/gaussScratch/${{scratchFolder}}/{data.jobname}.fchk {os.getcwd()}

    echo "Removing /localscratch/{data.user}/gaussScratch/${{scratchFolder}}"
    rm -rf "/localscratch/{data.user}/gaussScratch/${{scratchFolder}}"
}}
trap cleanup EXIT

#### BEGIN ####

cd $SLURM_SUBMIT_DIR
echo "I ran on: $SLURM_NODELIST"
echo "Starting at `date`"
NAME={data.jobname}

export DATADIR={os.getcwd()}
module purge

source /usr/local/sw/gauss/gauss{data.version}/g16.sh

export GAUSS_SCRDIR="/localscratch/{data.user}/gaussScratch/${{scratchFolder}}"
mkdir -p $GAUSS_SCRDIR
cp {os.getcwd()}/{data.jobname}.in $GAUSS_SCRDIR
cd $GAUSS_SCRDIR

/usr/bin/time -v gauss -slurm -np {data.mpisockets} -nt {data.ompthreads} {data.jobname}.in {data.jobname}.out

#Record keeping
echo "Finished at `date`"

mkdir -p "$DATADIR"
mkdir -p "$SCRATCH"
mkdir -p "$BIGSCRATCH"
mkdir -p "$GAUSS_SCRDIR"

cd "$SCRATCH"

export g16root={data.g16root}
source {data.g16root}/g16/bsd/g16.login

echo "I ran on: $SLURM_NODELIST"
echo "Available memory: `grep MemTotal /proc/meminfo`"
echo "Available storage: `df -h /localscratch`"
echo "Starting at `date`"

{data.g16root}/g16/g16 {data.inputfile}.com > {data.inputfile}.log
if [ $? ]; then
fi

"""
