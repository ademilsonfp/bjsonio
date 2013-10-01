# coding: utf-8

from setuptools import setup, find_packages

setup(
  name='flaskio',
  version='0.1-dev',
  author='Ademilson',
  author_email='ademilsonfp@gmail.com',
  install_requires=[
    'Flask==0.10'
  ],
  package_dir={'': 'src'},
  packages=find_packages('src', exclude=['test'])
)
