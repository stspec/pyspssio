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
import platform
from setuptools import setup

def read(*paths):
    with open(os.path.join(*paths), 'r') as f:
        return f.read()

package_data = {'pyspssio': ['README.*',
                             'LICENSE.*',
                             'spssio/document/*',
                             'spssio/include/*',
                             'spssio/license/*']}

pf_system = platform.system().lower()

# Windows 64
package_data['pyspssio'].append('spssio/win64/*.*')
# MacOS
package_data['pyspssio'].append('spssio/macos/*.*')
# Linux
package_data['pyspssio'].append('spssio/lin64/*.*')
#package_data['pyspssio'].append('spssio/plinux64/*.*')
#package_data['pyspssio'].append('spssio/zlinux64/*.*')

setup(
    name='pyspssio',
    version='0.2.1',
	description='Read and write SPSS (.sav and .zsav) files to/from pandas dataframes',
    long_description=read('README.md'),
    long_description_content_type='text/markdown',
	author="Steven Spector",
    author_email='stspec.dev@gmail.com',
    url='https://github.com/stspec/pyspssio',
    license='MIT',
    python_requires='>=3.6',
    install_requires=['pandas','psutil'],
    packages=['pyspssio'],
    package_data=package_data
)


