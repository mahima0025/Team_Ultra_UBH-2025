#!/usr/bin/env python3
import time
from grove.adc import ADC
from datetime import datetime

# Initialize ADC (Grove Base Hat handles analog input)
adc = ADC(address=0x04)

# Define the analog port (A2 by default)
LIGHT_SENSOR_CHANNEL = 2

def read_light_intensity():
    # Read raw ADC value (0–1023)
    value = adc.read(LIGHT_SENSOR_CHANNEL)

    # Convert to voltage (assuming 3.3V reference)
    voltage = value * 3.3 / 1023

    # Convert voltage to lux using approximate model
    lux = voltage_to_lux(voltage)

    return lux

def voltage_to_lux(voltage):
    # Example: lux = 500 * (voltage ** 1.5)
    # Replace with your fitted model after calibration
    return 500 * (voltage ** 1.5)

if __name__ == '__main__':
    print("Reading Grove Light Sensor v1.2...")
    tmstp = datetime.now().strftime('%M_%S')
    
    with open(f"/home/mahima/dev/Team_Ultra_UBH-2025/menu_optimiser/logs/lux_output_{tmstp}.txt", 'w') as f:
        while True:
            lux = read_light_intensity()
            f.write(f"{lux:.2f}\n")
            #print(f"Approximate Light Intensity: {lux:.2f} lux")
            print(f"{lux:.2f}")
            time.sleep(2)

