from setuptools import setup, find_packages
from os import path
from io import open

import versioneer

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(name='pynvml',
      version=versioneer.get_version(),
      cmdclass=versioneer.get_cmdclass(),
      python_requires='>=3.6',
      install_requires = ['nvidia-ml-py'],
      description='Python utilities for the NVIDIA Management Library',
      long_description=long_description,
      long_description_content_type='text/markdown',
      packages=find_packages(exclude=['notebooks', 'docs', 'tests']),
      package_data={'pynvml': ['README.md','help_query_gpu.txt']},
      license="BSD",
      url="http://www.nvidia.com/",
      author="NVIDIA Corporation",
      author_email="rzamora@nvidia.com",
      classifiers=[
          'Development Status :: 7 - Inactive',
          'Intended Audience :: Developers',
          'Intended Audience :: System Administrators',
          'License :: OSI Approved :: BSD License',
          'Operating System :: Microsoft :: Windows',
          'Operating System :: POSIX :: Linux',
          'Programming Language :: Python',
          'Topic :: Software Development :: Libraries :: Python Modules',
          'Topic :: System :: Hardware',
          'Topic :: System :: Systems Administration',
          ],
      )
