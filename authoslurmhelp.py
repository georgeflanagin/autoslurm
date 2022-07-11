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
# Other standard distro imports
###
import getpass
mynetid = getpass.getuser()

###
# From hpclib
###
from sloppytree import SloppyTree

###
# imports and objects that are a part of this project
###
verbose = False

###
# Credits
###
__author__ = 'Dominic Sirianni'
__copyright__ = 'Copyright 2022'
__credits__ = None
__version__ = 0.1
__maintainer__ = 'George Flanagin'
__email__ = 'gflanagi@richmond.edu'
__status__ = 'in progress'
__license__ = 'MIT'

helptext = SloppyTree()
helptext.description = """Automatically generate & queue
SLURM script(s) for running job(s) on Spydur."""
helptext.inputs = """Input file name(s) to run with Q-Chem. If more 
than one input file is provided, each will be submitted 
separately to the queue. If `all` requested, then all 
inputs in cwd will be submitted."""
helptext.mailtype = "Send SLURM status updates via email?"
helptext.mailuser = f"Different email than '{mynetid}@richmond.edu' to send status emails?"
helptext.jobname = "Different name than <jobname>.in under which to run job?"
helptext.cputotal = "Total number of CPUs to request from SLURM."
helptext.mem = "Total memory to request for job, in GB."
helptext.partition = "Partition/Queue to which job should be submitted."
helptext.exe = "Name of the primary program you are executing."
helptext.version = "Version of your primary program to run."
helptext.dryrun = "Just build the job script; do not try to run it."

