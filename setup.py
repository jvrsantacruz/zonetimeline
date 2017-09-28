# -*- coding: utf-8 -*-

import os

from setuptools import setup

here = os.path.dirname(os.path.abspath(__file__))
README = open(os.path.join(here, 'README.md')).read()
REQUIREMENTS = open(os.path.join(here, 'requirements.txt')).readlines()

setup(
    name='zonetimeline',
    version='0.1.0',
    description='Time zone timelines for the command line',
    author='Javier Santacruz',
    author_email='javier.santacruz.lc@gmail.com',
    install_requires=REQUIREMENTS,
    long_description=README,
    py_modules=['ztl'],
    classifiers=[
        "Internal :: Do not upload"
    ],
    entry_points="""
    [console_scripts]
    ztl=ztl:cli
    """
)
