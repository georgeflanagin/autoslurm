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
#       trunk -- the TLD where all the software for all the versions
#               is located.
#       root -- the subdirectory where the main executables are
#               found. There is considerable variety here.
###########################################################


programs.qchem.inputfiles = '*.in'
programs.qchem.versions = ('541', '53', ) 
programs.qchem.trunk = '/usr/local/sw/qchem/'
for v in programs.qchem.versions: 
    programs.qchem.root[v] = os.path.join(programs.qchem.trunk, f"qchem{v}")

programs.gaussian.inputfiles = '*.com'
programs.gaussian.versions = ('16B01', )
programs.gaussian.trunk = '/usr/local/sw/gaussian'
for v in programs.gaussian.versions:
    programs.gaussian.root[v] = os.path.join(programs.gaussian.trunk, f"g{v}/g16")


