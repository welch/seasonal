#!/usr/bin/env python
import os.path
from setuptools import setup

__version__ = "can't find version.py"
exec(compile(open('seasonal/version.py').read(), # pylint: disable=exec-used
                  'seasonal/version.py', 'exec'))

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(name='seasonal',
      version=__version__,
      description='Estimate trend and seasonal effects in a timeseries',
      author='Will Welch',
      author_email='github@quietplease.com',
      packages=['seasonal'],
      license="MIT",
      keywords="timeseries, seasonality, seasonal adjustment, detrend, robust estimation, theil-sen, Holt-Winters",
      url="https://github.com/welch/seasonal",
      long_description=read('README.rst'),
      classifiers=[
          "Development Status :: 4 - Beta",
          "License :: OSI Approved :: MIT License",
          "Programming Language :: Python :: 2.7",
          "Programming Language :: Python :: 3",
          "Topic :: Scientific/Engineering",
      ],
      install_requires=[
          "numpy",
          "scipy"
      ],
      tests_require=[
          "pytest",
          "pandas"
      ],
      extras_require={
          # all console_script entry points require pandas to read CSV.
          # additionally, if a console_script is to be invoked with
          # a --plot option, matplotlib must be installed.
          "CSV":  ["pandas"],
          "PLOT":  ["matplotlib"]
      },
      package_data={
          "seasonal": ["data/*"]
      },
      setup_requires=["pytest-runner"],
      entry_points={
          "console_scripts": [
              "seasonal = seasonal.application:seasonal_cmd [CSV]",
              "seasonal.trend = seasonal.application:trend_cmd [CSV]",
              "seasonal.periodogram = seasonal.application:periodogram_cmd [CSV]",
          ],
      }
)
