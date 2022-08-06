'''
	Python library for the ADS1115 Analog to Digital Converter
	Adapted by David H Hagan from Adafruit
	March 2015
	Contact: david@davidhhagan.com
	Adapted again by Alex K
	August 2022
'''

try:
	from setuptools import setup
except ImportError:
	from distutils.core import setup

setup(name='ADS1115',
      version='0.3.0',
      description='Python library for interacting with the ADS1115 Analog to Digital Converter.',
      url='http://github.com/vincentrou/ads1115_lib',
      author='Alex K',
      author_email='',
      license='MIT',
      keywords=['ADS1115', 'analog to digital converter', 'adc'],
      packages=['ADS1115'],
      install_requires=[
          'smbus2',
	  'RPi.GPIO'
	  ],
      zip_safe=False)
