#!/bin/bash

echo "Starting Tappa sync..."
cd /app
echo "-- Installing requirements"
pip install -r requirements.txt
echo "-- Running app"
python3 "app.py"