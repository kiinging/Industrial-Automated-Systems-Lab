#!/bin/bash

echo "Activate virtual environment"
source /home/orangepi/venv/bin/activate

echo "Navigate to your project directory"
cd /home/orangepi/projects/flask/

# Run app.py using sudo and virtualenv's python
echo "Starting temperature reading..."
$(which python) temp_reading.py &

echo "Starting Flask API..."
$(which python) web_api.py &