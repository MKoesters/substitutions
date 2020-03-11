#!/usr/bin/env python3
from setuptools import setup
import os

version_path = os.path.join(
    os.path.dirname(__file__),
    'substitutions',
    'version.txt'
)
with open(version_path, 'r') as version_file:
    version = version_file.read().strip()

with open('requirements.txt') as req_file:
    requirements = req_file.readlines()
 
setup(
    name             = 'substitutions',
    version          = version,
    packages         = ['substitutions'],
    package_dir      = {'substitutions': 'substitutions'},
    package_data     = {
        'substitutions': [
            'version.txt',
            'danger_mods'
        ]
    },
    entry_points={
        'console_scripts': [
            'substitutions = substitutions.run:main',
        ],
    },
    python_requires  = '>=3.5.0',
    install_requires = requirements,
    description      = '',
    long_description = '',
    author           = 'E. Mordret, M. Kösters',
    license          = 'The MIT license',
    platforms        = 'any that supports python 3.4',
    classifiers      = [
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Education',
        'Intended Audience :: Science/Research',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX',
        'Operating System :: POSIX :: SunOS/Solaris',
        'Operating System :: Unix',
        'Programming Language :: Python :: 3.4',
        'Topic :: Scientific/Engineering :: Bio-Informatics',
        'Topic :: Scientific/Engineering :: Chemistry',
        'Topic :: Scientific/Engineering :: Medical Science Apps.',
    ]
)
