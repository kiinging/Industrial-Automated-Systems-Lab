# 📷 Raspberry Pi Zero 2 W Security Camera (Flask + Picamera2)

This project sets up a lightweight **real-time video streaming server** on a Raspberry Pi Zero 2 W using **Flask** and **Picamera2**, without needing OpenCV. The system also supports auto-start on boot and is ready for remote access with Cloudflare Tunnel.

---

## ✅ What I Achieved:

- Live video streaming from Pi Camera using `picamera2` and Flask.
- Smooth browser display using MJPEG at ~10 FPS.
- Embedded timestamp overlay on each frame using PIL.
- Lightweight performance (RAM/CPU usage optimized for Zero 2 W).
- Optional auto-start using systemd.
- Verified remote access via Cloudflare Tunnel (DuckDNS not used).

---

## 🧪 Useful Commands & Tools

### 📸 Camera Test
```bash
libcamera-still -o test.jpg --width 640 --height 480
libcamera-hello
```
### 📊 System Monitoring
```bash
free         # Check RAM usage
htop         # View running processes
```

### 🛠️ Install Required Packages
```bash
sudo apt update
sudo apt install -y python3 python3-pip
sudo apt install -y python3-picamera2 libcamera-apps
```
### 🚀 Auto Start Flask App with systemd
Setup your Flask app to auto-start on boot using a custom .service file in /etc/systemd/system

## Duck dns is not used. it did not give me any advantage.
<!-- Ducker:
token: 7b72b777-cbac-4455-bfc9-b647e4e74e64
        zero2w.duckdns.org  -->