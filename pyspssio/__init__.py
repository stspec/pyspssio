# -*- coding: utf-8 -*-
# =============================================================================
# COPYRIGHT NOTICE
# =============================================================================
# 
# Copyright (c) 2022 Steven Spector
#
# The pyspssio python package is distributed under the MIT license, 
# EXCLUDING files from the IBM I/O Modules for SPSS Statistics 
# which are covered under a different license.
# 
# License information pertaining to the IBM I/O Modules for SPSS Statistics 
# is available in the LICENSE document.
# =============================================================================

import os
import sys
import platform

module_path = os.path.dirname(__file__)
sys.path.insert(0, module_path)

#from constants import *
#from spssfile import *
#from header import *
from reader import Reader
from writer import Writer
from user_functions import *

import config

pf_system = platform.system().lower()

# Windows 64
if pf_system.startswith('win'):
    spssio_folder = 'win64'
    spssio_module = 'spssio64.dll'

# MacOS
elif pf_system.startswith('darwin'):
    spssio_folder = 'macos'
    spssio_module = 'libspssdio.dylib'
    
# Linux
elif pf_system.startswith('lin'):
    spssio_folder = 'lin64'
    spssio_module = 'libspssdio.so.1'
    
try:
    config.spssio_module = os.path.join(module_path, 'spssio', spssio_folder, spssio_module)
except:
    pass
