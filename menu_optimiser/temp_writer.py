import math, sys, time, os
from grove.adc import ADC
from datetime import datetime

# Grove Temperature v1.2 defaults (10k NTC). Adjust BETA if needed.
VCC = 3.3
ADC_MAX = 4095
R_REF = 10000.0
THERMISTOR_NOMINAL = 10000.0
TEMP_NOMINAL = 25.0
BETA = 3380.0  # try 3950.0 if readings seem low

def adc_to_temp_c(adc_val):
    adc_val = max(1, min(adc_val, ADC_MAX - 1))
    v = (adc_val / ADC_MAX) * VCC
    r = R_REF * (v / (VCC - v))
    s = math.log(r / THERMISTOR_NOMINAL) / BETA + 1.0 / (TEMP_NOMINAL + 273.15)
    return v, r, (1.0 / s) - 273.15

def main():
    ch = int(sys.argv[1]) if len(sys.argv) > 1 else 0  # A0 by default
    # Use GROVE_I2C_BUS if set; otherwise library defaults to bus 1
    if "GROVE_I2C_BUS" not in os.environ:
        os.environ["GROVE_I2C_BUS"] = "1"
    adc = ADC(address=0x04)
    
    tmstmp = datetime.now().strftime('%M%S')
    with open(f'./logs/temp_logs_{tmstmp}.txt', 'w') as f:
        while True:
            val = adc.read(ch)
            v, r, t = adc_to_temp_c(val)
            print(f"ADC={val:4d}  V={v:0.3f}V  R={r:0.0f}Ω  T={t:0.2f}F")
            f.write(f'{t:.2f}\n')
            time.sleep(10)

if __name__ == "__main__":
    main()
