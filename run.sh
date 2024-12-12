#!/bin/bash

# Run app.py in the background
python3 app.py &

# Run forever.py in the background
python3 forever.py &

# Wait for all background processes to finish
# wait