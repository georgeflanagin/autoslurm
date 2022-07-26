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
helptext.cputotal = """
Total number of CPUs to request from SLURM. Keep in mind that
SLURM uses the term 'cpu' to mean 'core' in the current 
vernacular. 
"""
helptext.description = """
Automatically generate & queue SLURM script(s) for running job(s) on this cluster.
"""
helptext.dryrun = """
Just build the job script; do not try to run it. Note that if
autoslurm cannot write the slurm script, it will treat it as 
a dryrun, except that the script is echoed to the screen.
"""
helptext.exe = "Name of the primary program you are executing."
helptext.inputs = """
Data file spec(s) for the program you want to run. If more 
than one input file spec is provided, each will be submitted 
separately to the queue. If the file spec is a directory, then
the directory is searched for files with the right suffixes. 
If the file spec is a file, it will be assumed to be a data input 
file regardless of its name. Otherwise, the spec is globbed.
"""
helptext.jobname = "Different name than <jobname>.in under which to run job."
helptext.mailtype = "Send SLURM status updates via email."
helptext.mailuser = f"""
By default, your email address ({mynetid}@richmond.edu) will 
receive any emails. You can send them elsewhere.
"""
helptext.mem = "Total memory to request for job, in GB."
helptext.partition = """
Partition/Queue to which job should be submitted. Note that on
Spydur, your job might be relocated before it begins to run.
"""
helptext.version = """
Version of your primary program to run. If the version is 
omitted, then the latest version is assumed, and versions 
with higher version numbers are assumed to be "later."
"""

