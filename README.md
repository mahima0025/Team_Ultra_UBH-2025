# Pi 5 Grove Sensors (Miniconda, 64-bit)

Lightweight starter to run a **Raspberry Pi 5 (64-bit)** with **Grove analog sensors** (**Temperature v1.2** + **Light**) USB serial. Built for headless use over SSH. Comes with a minimal conda env for CPU ML/DL inference.

---

## Features
- ✅ Grove Temp v1.2 + Light via Arduino 101 (A0/A1) → JSON over `/dev/ttyACM*`
- ✅ Miniconda (Python 3.11) env for `onnxruntime` / `opencv` / `tflite-runtime` (optional)
- ✅ Headless-first (Lite OS); works on Desktop too

---

## Hardware
- **Raspberry Pi 5**, Raspberry Pi OS **Bookworm 64-bit** (Lite recommended)
- **Power**: Official 27 W USB-C
- **Arduino 101** (acts as ADC)
- **Grove sensors**: Temp v1.2 (thermistor), Light v1.2 (analog)
- **Wiring (Arduino 101)**  
  - Temp: `SIG→A0`, `VCC→5V`, `GND→GND`  
  - Light: `SIG→A1`, `VCC→5V`, `GND→GND`

---

## Repo structure
```
project/
├─ arduino/
│  └─ grove_sensors_arduino101.ino      # JSON: {"tempC":..,"light_raw":..,"light_norm":..}
├─ python/                
│  ├─ sensors_arduino.py                # read from /dev/ttyACM0
│  └─ main.py                           # combined camera + sensors demo
├─ environment.yml                      # conda env (python=3.11)
└─ README.md
```

---

## Quick start

### 1) Flash OS & first boot
1. Use **Raspberry Pi Imager** → **Raspberry Pi OS (64-bit) Lite**.  
2. ⚙️ Preconfigure: hostname, SSH, Wi-Fi (SSID/PW + country), username/password.  
3. Boot the Pi, then:
   ```bash
   ssh <user>@<hostname>.local
   sudo apt update && sudo apt full-upgrade -y && sudo reboot
   ```

### 2) System tools
```bash
sudo apt install -y v4l-utils git htop
sudo usermod -aG dialout $USER && newgrp dialout   # for Arduino serial
```

### 3) Miniconda (aarch64) & environment
```bash
cd ~
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-aarch64.sh
bash Miniconda3-latest-Linux-aarch64.sh -b -p $HOME/miniconda3
~/miniconda3/bin/conda init bash
exec $SHELL
conda config --add channels conda-forge
conda config --set channel_priority strict
# (optional) faster solver
conda install -n base -c conda-forge mamba -y

# Create env (or: mamba env create -f environment.yml)
conda create -n dl311 -c conda-forge -y   python=3.11 numpy scipy scikit-learn onnxruntime opencv pyserial pyyaml
conda activate dl311
# Optional: TensorFlow Lite
pip install --no-cache-dir tflite-runtime
```

### 4) Build & flash Arduino
- Open `arduino/grove_sensors_arduino101.ino` in the Arduino IDE and flash.  
- Serial output (115200 baud): `{"tempC":24.7,"light_raw":613,"light_norm":0.599}`

---

## Run

### Camera test
```bash
conda activate dl311
python python/camera_test.py
# writes frame.jpg if capture OK
```

### Sensors (Arduino) test
```bash
python python/sensors_arduino.py
# prints tempC / light values from /dev/ttyACM0
```

### Combined demo
```bash
python python/main.py
# logs camera status + sensor values every ~200 ms
```

---

## Connect over phone hotspot (SSH)
1. Connect **Pi and laptop** to the **same hotspot** (same SSID/band).  
2. Try: `ssh <user>@<hostname>.local`  
3. If needed, find the IP from the phone’s “Connected devices” (Android ~`192.168.43.x`, iOS ~`172.20.10.x`) and `ssh <user>@<PI_IP>`.

> Tip (NetworkManager): list APs `nmcli dev wifi list`, connect `nmcli dev wifi connect "SSID" password "PASS" ifname wlan0`.

---

## Troubleshooting
- **Camera missing**: `v4l2-ctl --list-devices`; try another USB port; check power.  
- **Serial permission**: `ls /dev/ttyACM*`; if denied: `sudo usermod -aG dialout $USER && newgrp dialout`.  
- **OpenCV import error** (in conda): `conda install -c conda-forge opencv`.  
- **Performance**: use 640×480 or 320×240; ensure cooling; use threaded capture if needed.

---

## License
MIT (or your choice).

-----

## Acknowledgments
- Raspberry Pi OS (Bookworm)  
- OpenCV, ONNX Runtime, TFLite (optional)  
- Seeed Grove sensors & Arduino 101
