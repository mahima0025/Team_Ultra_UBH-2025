import math, sys, time, os
from grove.adc import ADC

# Grove Temperature v1.2 defaults (10k NTC). Adjust BETA if needed.
VCC = 3.3
ADC_MAX = 4095
R_REF = 10000.0
THERMISTOR_NOMINAL = 10000.0
TEMP_NOMINAL = 25.0
BETA = 3380.0  # try 3950.0 if readings seem low

def c_to_f(c):
    return (c * 9/5) + 32

def f_to_c(f):
    return (f - 32) * 5/9

def adc_to_temp_c(adc_val):
    adc_val = max(1, min(adc_val, ADC_MAX - 1))
    v = (adc_val / ADC_MAX) * VCC
    # protect against divide-by-zero if v≈VCC
    v = max(1e-9, min(v, VCC - 1e-9))
    r = R_REF * (v / (VCC - v))
    s = math.log(r / THERMISTOR_NOMINAL) / BETA + 1.0 / (TEMP_NOMINAL + 273.15)
    return v, r, (1.0 / s) - 273.15

def main():
    ch = int(sys.argv[1]) if len(sys.argv) > 1 else 0  # A0 by default
    # Use GROVE_I2C_BUS if set; otherwise library defaults to bus 1
    if "GROVE_I2C_BUS" not in os.environ:
        os.environ["GROVE_I2C_BUS"] = "1"
    adc = ADC()
    while True:
        val = adc.read(ch)
        v, r, t_c = adc_to_temp_c(val)
        t_f = c_to_f(t_c)
        print(f"ADC={val:4d}  V={v:0.3f}V  R={r:0.0f}Ω  T={t_c:0.2f}°C / {t_f:0.2f}°F")
        time.sleep(1)

if __name__ == "__main__":
    main()
