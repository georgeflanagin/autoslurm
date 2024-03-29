# -*- coding: utf-8 -*-
"""
Information about the programs installed on Spydur.
"""

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
from sloppytree import SloppyTree

###
# Credits
###
__author__ = 'George Flanagin'
__copyright__ = 'Copyright 2022, Univeristy of Richmond.'
__credits__ = None
__version__ = 0.1
__maintainer__ = 'George Flanagin'
__email__ = 'gflanagin@richmond.edu'
__status__ = 'in progress'
__license__ = 'MIT'

programs = SloppyTree()

###########################################################
# How the tree is organized:
#
# The keys are the commonsense names of the programs.
#   The subkeys are:
#       inputfiles -- the pattern for the input file names
#       versions -- the names of the versions that are installed.
#       cpus -- reasonable maximum cpus
#       mem -- reasonable maximum GB of memory
#       exe -- the location of the primary executable.
###########################################################

programs.amber.inputfiles = "*.inpcrd"
programs.amber.versions = ('20', )
programs.amber.cpus = 10
programs.amber.mem = 50
for v in programs.amber.versions:
    programs.amber.exe[v] = f'/usr/local/sw/amber/amber{v}/amber.sh'

programs.qchem.inputfiles = '*.in'
programs.qchem.versions = ('541', '53', ) 
programs.qchem.cpus = 20
programs.qchem.mem = 100
for v in programs.qchem.versions: 
    programs.qchem.exe[v] = f"/usr/local/sw/qchem/qchem{v}/qchem"

programs.gaussian.inputfiles = '*.com'
programs.gaussian.versions = ('16B01', )
programs.gaussian.cpus = 16
programs.gaussian.mem = 32
for v in programs.gaussian.versions:
    programs.gaussian.exe[v] = f"/usr/local/sw/gaussian/g{v}/g16/g16"


