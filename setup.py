from distutils.core import setup
import os

with open(os.path.join(os.path.dirname(__file__), 'requirements.txt')) as f:
    requirements = f.read().splitlines()

setup(name='finicity-python',
      version='0.1',
      description='Python wrapper for Finicity API',
      author='',
      author_email='',
      url='',
      packages=['finicity'],
      package_dirs = {'finicity' : 'finicity'},
      install_requires=requirements,
     )