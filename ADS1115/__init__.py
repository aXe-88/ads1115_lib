import time
import smbus2
# import threading
import RPi.GPIO as GPIO

__all__ = ['ADS1115']

# ===========================================================================
# ADS1115 Class
# ===========================================================================
class ADS1115:
    i2c = None

    # IC Identifiers
    __IC_ADS1115 = 0x01

    # gpio_event = threading.Event()
    # gpio_event.clear()

    # Config Register
    __ADS1115_REG_CONFIG_DR_SHIFT     = 5
    __ADS1115_REG_CONFIG_DR_MASK      = 0x00E0
    __ADS1115_REG_CONFIG_DR_8SPS      = 0x0000  # 8 samples per second
    __ADS1115_REG_CONFIG_DR_16SPS     = 0x0020  # 16 samples per second
    __ADS1115_REG_CONFIG_DR_32SPS     = 0x0040  # 32 samples per second
    __ADS1115_REG_CONFIG_DR_64SPS     = 0x0060  # 64 samples per second
    __ADS1115_REG_CONFIG_DR_128SPS    = 0x0080  # 128 samples per second
    __ADS1115_REG_CONFIG_DR_250SPS    = 0x00A0  # 250 samples per second (default)
    __ADS1115_REG_CONFIG_DR_475SPS    = 0x00C0  # 475 samples per second
    __ADS1115_REG_CONFIG_DR_860SPS    = 0x00E0  # 860 samples per second

    __ADS1015_REG_CONFIG_CQUE_SHIFT   = 0
    __ADS1015_REG_CONFIG_CQUE_MASK    = 0x0003
    __ADS1015_REG_CONFIG_CQUE_1CONV   = 0x0000  # Assert ALERT/RDY after one conversions
    __ADS1015_REG_CONFIG_CQUE_2CONV   = 0x0001  # Assert ALERT/RDY after two conversions
    __ADS1015_REG_CONFIG_CQUE_4CONV   = 0x0002  # Assert ALERT/RDY after four conversions
    __ADS1015_REG_CONFIG_CQUE_NONE    = 0x0003  # Disable the comparator and put ALERT/RDY in high state (default)

    __ADS1015_REG_CONFIG_CMODE_SHIFT  = 4
    __ADS1015_REG_CONFIG_CMODE_MASK   = 0x0010
    __ADS1015_REG_CONFIG_CMODE_TRAD   = 0x0000  # Traditional comparator with hysteresis (default)
    __ADS1015_REG_CONFIG_CMODE_WINDOW = 0x0010  # Window comparator

    __ADS1015_REG_CONFIG_CPOL_SHIFT   = 3
    __ADS1015_REG_CONFIG_CPOL_MASK    = 0x0008
    __ADS1015_REG_CONFIG_CPOL_ACTVLOW = 0x0000  # ALERT/RDY pin is low when active (default)
    __ADS1015_REG_CONFIG_CPOL_ACTVHI  = 0x0008  # ALERT/RDY pin is high when active

    __ADS1015_REG_CONFIG_CLAT_SHIFT   = 2
    __ADS1015_REG_CONFIG_CLAT_MASK    = 0x0004  # Determines if ALERT/RDY pin latches once asserted
    __ADS1015_REG_CONFIG_CLAT_NONLAT  = 0x0000  # Non-latching comparator (default)
    __ADS1015_REG_CONFIG_CLAT_LATCH   = 0x0004  # Latching comparator

    __ADS1015_REG_CONFIG_MODE_SHIFT   = 8
    __ADS1015_REG_CONFIG_MODE_MASK    = 0x0100
    __ADS1015_REG_CONFIG_MODE_CONTIN  = 0x0000  # Continuous conversion mode
    __ADS1015_REG_CONFIG_MODE_SINGLE  = 0x0100  # Power-down single-shot mode (default)

    __ADS1015_REG_CONFIG_PGA_SHIFT    = 9
    __ADS1015_REG_CONFIG_PGA_MASK     = 0x0E00
    __ADS1015_REG_CONFIG_PGA_6_144V   = 0x0000  # +/-6.144V range
    __ADS1015_REG_CONFIG_PGA_4_096V   = 0x0200  # +/-4.096V range
    __ADS1015_REG_CONFIG_PGA_2_048V   = 0x0400  # +/-2.048V range (default)
    __ADS1015_REG_CONFIG_PGA_1_024V   = 0x0600  # +/-1.024V range
    __ADS1015_REG_CONFIG_PGA_0_512V   = 0x0800  # +/-0.512V range
    __ADS1015_REG_CONFIG_PGA_0_256V   = 0x0A00  # +/-0.256V range

    __ADS1015_REG_CONFIG_MUX_SHIFT    = 12
    __ADS1015_REG_CONFIG_MUX_MASK     = 0x7000
    __ADS1015_REG_CONFIG_MUX_DIFF_0_1 = 0x0000  # Differential P = AIN0, N = AIN1 (default)
    __ADS1015_REG_CONFIG_MUX_DIFF_0_3 = 0x1000  # Differential P = AIN0, N = AIN3
    __ADS1015_REG_CONFIG_MUX_DIFF_1_3 = 0x2000  # Differential P = AIN1, N = AIN3
    __ADS1015_REG_CONFIG_MUX_DIFF_2_3 = 0x3000  # Differential P = AIN2, N = AIN3
    __ADS1015_REG_CONFIG_MUX_SINGLE_0 = 0x4000  # Single-ended AIN0
    __ADS1015_REG_CONFIG_MUX_SINGLE_1 = 0x5000  # Single-ended AIN1
    __ADS1015_REG_CONFIG_MUX_SINGLE_2 = 0x6000  # Single-ended AIN2
    __ADS1015_REG_CONFIG_MUX_SINGLE_3 = 0x7000  # Single-ended AIN3

     # Config Register
    __ADS1015_REG_CONFIG_OS_MASK      = 0x8000
    __ADS1015_REG_CONFIG_OS_SINGLE    = 0x8000  # Write: Set to start a single-conversion
    __ADS1015_REG_CONFIG_OS_BUSY      = 0x0000  # Read: Bit = 0 when conversion is in progress
    __ADS1015_REG_CONFIG_OS_NOTBUSY   = 0x8000  # Read: Bit = 1 when device is not performing a conversion

    # Pointer Register
    __ADS1015_REG_POINTER_MASK        = 0x03
    __ADS1015_REG_POINTER_CONVERT     = 0x00
    __ADS1015_REG_POINTER_CONFIG      = 0x01
    __ADS1015_REG_POINTER_LOWTHRESH   = 0x02
    __ADS1015_REG_POINTER_HITHRESH    = 0x03
    
    # Dictionaries with the sampling speed values
    # These simplify and clean the code (avoid the abuse of if/elif/else clauses)
    spsADS1115 = {
        8:__ADS1115_REG_CONFIG_DR_8SPS,
        16:__ADS1115_REG_CONFIG_DR_16SPS,
        32:__ADS1115_REG_CONFIG_DR_32SPS,
        64:__ADS1115_REG_CONFIG_DR_64SPS,
        128:__ADS1115_REG_CONFIG_DR_128SPS,
        250:__ADS1115_REG_CONFIG_DR_250SPS,
        475:__ADS1115_REG_CONFIG_DR_475SPS,
        860:__ADS1115_REG_CONFIG_DR_860SPS
        }   

    # Dictionariy with the programable gains
    pgaADS1x15 = {
        6144:__ADS1015_REG_CONFIG_PGA_6_144V,
        4096:__ADS1015_REG_CONFIG_PGA_4_096V,
        2048:__ADS1015_REG_CONFIG_PGA_2_048V,
        1024:__ADS1015_REG_CONFIG_PGA_1_024V,
        512:__ADS1015_REG_CONFIG_PGA_0_512V,
        256:__ADS1015_REG_CONFIG_PGA_0_256V
        }  

    # def gpioCallback(self,channel):
    #     #print("hit")
    #     self.gpio_event.set()

    # Constructor
    def __init__(self, address=0x48, ic=__IC_ADS1115, debug=False, i2c=None, rdy_pin=None, timing=False):
        if not i2c: #isinstance(i2c,smbus2.SMBus):
            try:
                self.i2c = smbus2.SMBus(1)
            except:
                raise IOError("Could not find i2c device")
        else:
            self.i2c = i2c
        self.address = address
        self.debug = debug
        self.timing = timing

        # Make sure the IC specified is valid
        if (ic > self.__IC_ADS1115):
            return -1
        else:
            self.ic = ic
            
        # Setup GPIO
        if not rdy_pin:
            self.sw_timing = True
            self.hithresh = [0x7f,0xff]
            self.lothresh = [0x80,0x00]
        else:
            self.sw_timing = False
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(rdy_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            # GPIO.add_event_detect(rdy_pin, GPIO.FALLING, self.gpioCallback)
            self.rdy_pin = rdy_pin
            self.hithresh = [0x80,0x00]
            self.lothresh = [0x7f,0xff]

        self.i2c.write_i2c_block_data(self.address, self.__ADS1015_REG_POINTER_HITHRESH, self.hithresh)
        self.i2c.write_i2c_block_data(self.address, self.__ADS1015_REG_POINTER_LOWTHRESH, self.lothresh)

        if self.debug == True:
            rb_hi = self.i2c.read_i2c_block_data(self.address, self.__ADS1015_REG_POINTER_HITHRESH, 2)
            rb_lo = self.i2c.read_i2c_block_data(self.address, self.__ADS1015_REG_POINTER_LOWTHRESH, 2)
            print("HI   " + hex(rb_hi[0]<<8 | rb_hi[1]))
            print("LO   " + hex(rb_lo[0]<<8 | rb_lo[1]))
            
        # Set pga value, so that getLastConversionResult() can use it,
        # any function that accepts a pga value must update this.
        self.pga = 6144
        
    def __del__(self):
        if self.sw_timing == False:
            GPIO.cleanup()

    def setupMultiChannelRead(self, pga=6144, sps=250):
        if self.sw_timing == True:
            # Disable comparator, Non-latching, Alert/Rdy active low
            # traditional comparator, single-shot mode
            self.mc_config = self.__ADS1015_REG_CONFIG_CQUE_NONE    | \
                    self.__ADS1015_REG_CONFIG_CLAT_NONLAT  | \
                    self.__ADS1015_REG_CONFIG_CPOL_ACTVLOW | \
                    self.__ADS1015_REG_CONFIG_CMODE_TRAD   | \
                    self.__ADS1015_REG_CONFIG_MODE_SINGLE   
        else:
            # Disable comparator, Non-latching, Alert/Rdy active low
            # traditional comparator, single-shot mode, alrt after 1 conv
            self.mc_config = self.__ADS1015_REG_CONFIG_CQUE_1CONV    | \
                    self.__ADS1015_REG_CONFIG_CLAT_NONLAT  | \
                    self.__ADS1015_REG_CONFIG_CPOL_ACTVLOW | \
                    self.__ADS1015_REG_CONFIG_CMODE_TRAD   | \
                    self.__ADS1015_REG_CONFIG_MODE_SINGLE  
        # Set sample per seconds, defaults to 250sps
        self.mc_config |= self.spsADS1115.setdefault(sps, self.__ADS1115_REG_CONFIG_DR_250SPS)
        self.sps = sps

        # Set PGA/voltage range, defaults to +-6.144V  
        self.mc_config |= self.pgaADS1x15.setdefault(pga, self.__ADS1015_REG_CONFIG_PGA_6_144V)
        self.pga = pga

        # Set 'start single-conversion' bit
        self.mc_config |= self.__ADS1015_REG_CONFIG_OS_SINGLE
        
        if self.debug == True:
            #print("MUX  " + bin((self.mc_config & self.__ADS1015_REG_CONFIG_MUX_MASK)>>self.__ADS1015_REG_CONFIG_MUX_SHIFT))
            print("PGA  " + bin((self.mc_config & self.__ADS1015_REG_CONFIG_PGA_MASK)>>self.__ADS1015_REG_CONFIG_PGA_SHIFT))
            print("MODE " + bin((self.mc_config & self.__ADS1015_REG_CONFIG_MODE_MASK)>>self.__ADS1015_REG_CONFIG_MODE_SHIFT))
            print("DR   " + bin((self.mc_config & self.__ADS1115_REG_CONFIG_DR_MASK)>>self.__ADS1115_REG_CONFIG_DR_SHIFT))
            print("CM   " + bin((self.mc_config & self.__ADS1015_REG_CONFIG_CMODE_MASK)>>self.__ADS1015_REG_CONFIG_CMODE_SHIFT))
            print("CP   " + bin((self.mc_config & self.__ADS1015_REG_CONFIG_CPOL_MASK)>>self.__ADS1015_REG_CONFIG_CPOL_SHIFT))
            print("CL   " + bin((self.mc_config & self.__ADS1015_REG_CONFIG_CLAT_MASK)>>self.__ADS1015_REG_CONFIG_CLAT_SHIFT))
            print("CQUE " + bin((self.mc_config & self.__ADS1015_REG_CONFIG_CQUE_MASK)>>self.__ADS1015_REG_CONFIG_CQUE_SHIFT))
        
    def readADCMultiSingleEnded(self):           
        if self.timing:
            timeEnter = time.time_ns()
        
        retval = [None] * 4

        config = self.mc_config | self.__ADS1015_REG_CONFIG_MUX_SINGLE_0

        # Write config register to the ADC
        bytes = [(config >> 8) & 0xFF, config & 0xFF]
        # self.gpio_event.clear()
        self.i2c.write_i2c_block_data(self.address, self.__ADS1015_REG_POINTER_CONFIG, bytes)

        #config for next iter
        config = self.mc_config | self.__ADS1015_REG_CONFIG_MUX_SINGLE_1
        bytes = [(config >> 8) & 0xFF, config & 0xFF]
        # Wait for the ADC conversion to complete
        # The minimum delay depends on the sps: delay >= 1/sps
        # We add 0.1ms to be sure
        
        delay = 1.0/self.sps+0.0001
        if self.sw_timing == True:
            time.sleep(delay)
        else:            
            #if self.gpio_event.wait(timeout=int(1000*delay))==False:
            #    print("not hit")
            while GPIO.input(self.rdy_pin) == GPIO.HIGH:
                pass
        
        # Read the conversion results
        result = self.i2c.read_i2c_block_data(self.address, self.__ADS1015_REG_POINTER_CONVERT, 2)
        #self.gpio_event.clear()
        self.i2c.write_i2c_block_data(self.address, self.__ADS1015_REG_POINTER_CONFIG, bytes)

        val = (result[0] << 8) | (result[1])
        if val > 0x7FFF:
            retval[0] = (val - 0xFFFF)*self.pga/32768.0
        else:
            retval[0] = ( (result[0] << 8) | (result[1]) )*self.pga/32768.0

        #config for next iter
        config = self.mc_config | self.__ADS1015_REG_CONFIG_MUX_SINGLE_2
        bytes = [(config >> 8) & 0xFF, config & 0xFF]

        if self.sw_timing == True:
            time.sleep(delay)
        else:            
            # if self.gpio_event.wait(timeout=int(1000*delay))==False:
            #     print("not hit")
            while GPIO.input(self.rdy_pin) == GPIO.HIGH:
                pass

        result = self.i2c.read_i2c_block_data(self.address, self.__ADS1015_REG_POINTER_CONVERT, 2)
        # self.gpio_event.clear()
        self.i2c.write_i2c_block_data(self.address, self.__ADS1015_REG_POINTER_CONFIG, bytes)

        val = (result[0] << 8) | (result[1])
        if val > 0x7FFF:
            retval[1] = (val - 0xFFFF)*self.pga/32768.0
        else:
            retval[1] = ( (result[0] << 8) | (result[1]) )*self.pga/32768.0

        #config for next iter
        config = self.mc_config | self.__ADS1015_REG_CONFIG_MUX_SINGLE_3
        bytes = [(config >> 8) & 0xFF, config & 0xFF]

        if self.sw_timing == True:
            time.sleep(delay)
        else:            
            # if self.gpio_event.wait(timeout=int(1000*delay))==False:
                # print("not hit")
            while GPIO.input(self.rdy_pin) == GPIO.HIGH:
                pass

        result = self.i2c.read_i2c_block_data(self.address, self.__ADS1015_REG_POINTER_CONVERT, 2)
        # self.gpio_event.clear()
        self.i2c.write_i2c_block_data(self.address, self.__ADS1015_REG_POINTER_CONFIG, bytes)
        
        val = (result[0] << 8) | (result[1])
        if val > 0x7FFF:
            retval[2] = (val - 0xFFFF)*self.pga/32768.0
        else:
            retval[2] = ( (result[0] << 8) | (result[1]) )*self.pga/32768.0

        if self.sw_timing == True:
            time.sleep(delay)
        else:            
            # if self.gpio_event.wait(timeout=int(1000*delay))==False:
            #     print("not hit")
            while GPIO.input(self.rdy_pin) == GPIO.HIGH:
                pass
            
        result = self.i2c.read_i2c_block_data(self.address, self.__ADS1015_REG_POINTER_CONVERT, 2)
        
        val = (result[0] << 8) | (result[1])
        if val > 0x7FFF:
            retval[3] = (val - 0xFFFF)*self.pga/32768.0
        else:
            retval[3] = ( (result[0] << 8) | (result[1]) )*self.pga/32768.0
    
        
        if self.timing:
            ttime = (time.time_ns() - timeEnter)/1e6
            #print("TIME " + str(ttime) + " ms")
            #print(retval)
            return ttime

        #print(retval)
        return retval
    
    def readADCSingleEnded(self, channel=0, pga=6144, sps=250):
        ''' 
            Gets a single-ended ADC reading from the specified channel in mV. 
            The sample rate for this mode (single-shot) can be used to lower the noise 
            (low sps) or to lower the power consumption (high sps) by duty cycling, 
            see datasheet page 14 for more info. 
            The pga must be given in mV, see page 13 for the supported values. 
        '''
        if self.timing:
            timeEnter = time.time_ns()

        # With invalid channel return -1
        if (channel > 3):
            return -1
    
        # Disable comparator, Non-latching, Alert/Rdy active low
        # traditional comparator, single-shot mode
        if self.sw_timing == True:
            config = self.__ADS1015_REG_CONFIG_CQUE_NONE   | \
                    self.__ADS1015_REG_CONFIG_CLAT_NONLAT  | \
                    self.__ADS1015_REG_CONFIG_CPOL_ACTVLOW | \
                    self.__ADS1015_REG_CONFIG_CMODE_TRAD   | \
                    self.__ADS1015_REG_CONFIG_MODE_SINGLE   
        else:
            config = self.__ADS1015_REG_CONFIG_CQUE_1CONV  | \
                    self.__ADS1015_REG_CONFIG_CLAT_NONLAT  | \
                    self.__ADS1015_REG_CONFIG_CPOL_ACTVLOW | \
                    self.__ADS1015_REG_CONFIG_CMODE_TRAD   | \
                    self.__ADS1015_REG_CONFIG_MODE_SINGLE  

        # Set sample per seconds, defaults to 250sps
        config |= self.spsADS1115.setdefault(sps, self.__ADS1115_REG_CONFIG_DR_250SPS)
        self.sps = sps

        # Set PGA/voltage range, defaults to +-6.144V  
        config |= self.pgaADS1x15.setdefault(pga, self.__ADS1015_REG_CONFIG_PGA_6_144V)
        self.pga = pga

        # Set the channel to be converted
        if channel == 3:
            config |= self.__ADS1015_REG_CONFIG_MUX_SINGLE_3
        elif channel == 2:
            config |= self.__ADS1015_REG_CONFIG_MUX_SINGLE_2
        elif channel == 1:
            config |= self.__ADS1015_REG_CONFIG_MUX_SINGLE_1
        else:
            config |= self.__ADS1015_REG_CONFIG_MUX_SINGLE_0

        # Set 'start single-conversion' bit
        config |= self.__ADS1015_REG_CONFIG_OS_SINGLE

        if self.debug == True:
            #print(hex(config))
            #print(bin(config))

            print("MUX  " + bin((config & self.__ADS1015_REG_CONFIG_MUX_MASK)>>self.__ADS1015_REG_CONFIG_MUX_SHIFT))
            print("PGA  " + bin((config & self.__ADS1015_REG_CONFIG_PGA_MASK)>>self.__ADS1015_REG_CONFIG_PGA_SHIFT))
            print("MODE " + bin((config & self.__ADS1015_REG_CONFIG_MODE_MASK)>>self.__ADS1015_REG_CONFIG_MODE_SHIFT))
            print("DR   " + bin((config & self.__ADS1115_REG_CONFIG_DR_MASK)>>self.__ADS1115_REG_CONFIG_DR_SHIFT))
            print("CM   " + bin((config & self.__ADS1015_REG_CONFIG_CMODE_MASK)>>self.__ADS1015_REG_CONFIG_CMODE_SHIFT))
            print("CP   " + bin((config & self.__ADS1015_REG_CONFIG_CPOL_MASK)>>self.__ADS1015_REG_CONFIG_CPOL_SHIFT))
            print("CL   " + bin((config & self.__ADS1015_REG_CONFIG_CLAT_MASK)>>self.__ADS1015_REG_CONFIG_CLAT_SHIFT))
            print("CQUE " + bin((config & self.__ADS1015_REG_CONFIG_CQUE_MASK)>>self.__ADS1015_REG_CONFIG_CQUE_SHIFT))

        # Write config register to the ADC
        bytes = [(config >> 8) & 0xFF, config & 0xFF]
        #self.gpio_event.clear()
        self.i2c.write_i2c_block_data(self.address, self.__ADS1015_REG_POINTER_CONFIG, bytes)

        # Wait for the ADC conversion to complete
        # The minimum delay depends on the sps: delay >= 1/sps
        # We add 0.1ms to be sure
        delay = 1.0/sps+0.0001
        if self.sw_timing == True:
            time.sleep(delay)
        else:            
            # if self.gpio_event.wait(timeout=int(1000*delay))==False:
            #     print("not hit")
            
            while GPIO.input(self.rdy_pin) == GPIO.HIGH:
                pass

        # Read the conversion results
        result = self.i2c.read_i2c_block_data(self.address, self.__ADS1015_REG_POINTER_CONVERT, 2)
        # Return a mV value for the ADS1115
        # (Take signed values into account as well)
        val = (result[0] << 8) | (result[1])
        if val > 0x7FFF:
            retval = (val - 0xFFFF)*pga/32768.0
        else:
            retval = ( (result[0] << 8) | (result[1]) )*pga/32768.0

        if self.timing:
            print("TIME " + str((time.time_ns() - timeEnter)/1e6) + " ms")
        return retval
