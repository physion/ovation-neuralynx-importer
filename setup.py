#!/usr/bin/env python

from distutils.core import setup

setup(name='Ovation Neuralynx Import',
    version='1.0',
    description='Neuralynx importer for Physion Ovation',
    url='https://github.com/physion/ovation-neuralynx-importer',
    author='Physion Consulting',
    author_email='info@physionconsulting.com',
    packages=['ovneuralynx'],
    package_dir = {'': 'neuralynx-import'},
    scripts=['neuralynx-import/bin/osx-neuralynx-import',
             'neuralynx-import/bin/linux-neuralynx-import',
             'neuralynx-import/bin/windows-neuralynx-import']
)
