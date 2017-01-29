#!/usr/bin/env python
from setuptools import setup, find_packages

setup(
    name='simple_transactions',
    description='',
    url='',
    version='1.0',
    include_package_data=True,

    packages=find_packages(
        exclude=['*tests', 'tests*', '*.tests.*', 'tests']
    ),
    zip_safe=True,
    install_requires=[
        'django',
        'django-filter',
        'architect',
        'psycopg2'
    ],
)
