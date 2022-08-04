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

###################################### DATE ##########################

slurm.date = lambda data : f"""#!/bin/bash -e
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

cd $SLURM_SUBMIT_DIR
echo "I ran on: $SLURM_NODELIST"
echo "Starting at `date`"

NAME={data.jobname}

/usr/bin/time -v {data.program} 

echo "Finished at `date`"

"""

##################################### QCHEM ##########################

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

export DATADIR={data.defaultdir}

export GAUSS_SCRDIR="/localscratch/{data.user}/gaussScratch/${{scratchFolder}}"
mkdir -p $GAUSS_SCRDIR
cp {data.defaultdir}/{data.jobname}.in $GAUSS_SCRDIR
cd $GAUSS_SCRDIR

{data.program} {data.inp} > {data.inp}.log

echo "Finished at `date`"
"""

################################### GAUSSIAN ##########################

slurm.amber = lambda data : f"""#!/bin/bash -e

#SBATCH --job-name=T1_A100
#SBATCH --output=T1_A100.txt
#SBATCH --partition=ML
#SBATCH --gres=gpu:tesla_a100:1
#SBATCH --ntasks=1
#SBATCH --time=00:00:00

# Print the simulation start date/time
date


# Print the GPU node the simulation is running on
echo "I ran on:"
cd $SLURM_SUBMIT_DIR
echo "SLURM_NODELIST=$SLURM_NODELIST"

# Load the necessary program libraries

source /usr/local/sw/amber/amber20/amber.sh
#setenv CUDA_HOME /usr/local/cuda-11.4
export CUDA_HOME="/usr/local/cuda-11.4"
export CUDA_VISIBLE_DEVICES=0
export PYTHONPATH="/usr/local/sw/amber/amber20/lib/python3.8/site-packages:$PYTHONPATH"
export PATH="/usr/local/sw/amber/amber20/bin:$PATH"
export LD_LIBRARY_PATH="/usr/local/sw/amber/amber20/lib:/usr/local/cuda/lib64:/usr/local/cuda/lib64/stubs:$LD_LIBRARY_PATH"

env | sort

# Set the output file directory
#cd /work/ja9ia/Si_POSS/PM6/MethoxyIndene/S1

# Run Amber Jobs
./min.sh
./heat.sh
./eq.sh
./md.sh

# Print the simulation end date/time
date
"""
