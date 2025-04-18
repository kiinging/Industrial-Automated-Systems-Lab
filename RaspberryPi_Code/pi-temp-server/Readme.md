orangepi-temp-server/
├── sensor.py          ← Reads data from MAX31865 & MAX31855
├── web_api.py         ← Flask API for LED control (Cloudflare Worker)
├── shared_data.py     ← Global variable storage (temperature values, etc.)
├── run_all.sh         ← Start script (run everything)
└── requirements.txt   ← Python dependencies (optional but recommended)
