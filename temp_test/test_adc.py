# save as which_hat_addr.py and run:  python which_hat_addr.py
# Requires: pip install grove.py smbus2 RPi.GPIO

def try_probe(addr):
    try:
        # grove.py usually exposes ADC here:
        try:
            from grove.adc import ADC          # common path
        except ImportError:
            from adc import ADC                 # fallback if module layout differs

        adc = ADC(address=addr)                 # NOTE: no 'bus=' kwarg
        # Try a simple read; channel 0 exists even with nothing plugged
        _ = adc.read(0)                         # or adc.read_voltage(0) on some versions
        print(f"✅ Found Grove Base Hat ADC at {hex(addr)}")
        return True
    except Exception as e:
        print(f"❌ {hex(addr)} not responding: {e}")
        return False

for a in (0x04, 0x08):
    if try_probe(a):
        break

