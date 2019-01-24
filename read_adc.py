import ADS1115
import time

ads = ADS1115.ADS1115()

while True:
    volt = ads.readADCSingleEnded()
    
    print("{:.0f} mV mesuré sur AN0".format(volt))
    
    time.sleep(0.1)
    