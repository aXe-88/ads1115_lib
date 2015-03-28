#!/usr/bin/python3

from ADS1115 import ADS1115

ADS1115 = 0x01	# 16-bit ADC

# Select the gain
gain = 6144  # +/- 6.144V

# Select the sample rate
sps = 250  # 250 samples per second

# Initialise the ADC using the default mode (use default I2C address)
# Set this to ADS1015 or ADS1115 depending on the ADC you are using!
adc = ADS1115(ic=ADS1115)

# Read channel 0 in single-ended mode using the settings above
volts = adc.readADCSingleEnded(0, gain, sps) / 1000

print ("0".format(volts))