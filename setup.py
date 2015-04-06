'''
	Python library for the ADS1115 Analog to Digital Converter
	Adapted by David H Hagan from Adafruit
	March 2015
	Contact: david@davidhhagan.com
'''

try:
	from setuptools import setup
except ImportError:
	from distutils.core import setup

setup(name='ADS1115',
      version='0.1.11',
      description='Python library for interacting with the ADS1115 Analog to Digital Converter.',
      url='http://github.com/dhhagan/Adafruit-Raspberry-Pi-Python-Code',
      author='David H Hagan',
      author_email='david@davidhhagan.com',
      license='MIT',
	  keywords=['ADS1115', 'analog to digital converter', 'adc'],
      packages=['ADS1115',
			],
	  install_requires=[
	  ],
      zip_safe=False)