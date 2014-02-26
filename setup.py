#!/usr/bin/env python

from setuptools import setup

LONG_DESCRIPTION = """This packages provides Ovation importers for Neuralynx formats.

An ovation.io account and the ovation-python library is required for use.
"""

setup(name='Ovation Neuralynx Import',
    version='2.0-alpha',
    description='Neuralynx importer for Physion Ovation',
    long_description=LONG_DESCRIPTION,
    author='Physion',
    author_email='info@physion.us',
    url='https://github.com/physion/ovation-neuralynx-importer',
    packages=['ovation_neuralynx'],
    install_requires=['ovation>=2.1.8'],
    tests_require=['nose==1.3.0'],
    classifiers=[
        'Development Status :: 5 - Alpha',
        'Environment :: Console',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Science/Research',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Programming Language :: Python',
    ],
    scripts=['bin/osx-neuralynx-import',
             'bin/linux-neuralynx-import',
             'bin/windows-neuralynx-import']
)
