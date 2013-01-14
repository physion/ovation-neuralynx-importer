#!/usr/bin/env python

from distutils.core import setup

setup(name='Ovation Neuralynx Import',
    version='1.0',
    description='Neuralynx importer for Physion Ovation',
    author='Physion Consulting',
    author_email='info@physionconsulting.com',
    packages=['ovneuralynx'],
    package_dir = {'': 'neuralynx-import'}
)
