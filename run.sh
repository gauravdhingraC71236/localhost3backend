#!/bin/bash

# Create a virtual environment
python -m venv venv

# Activate the virtual environment
if [[ "$OSTYPE" == "msys" ]]; then
    # On Windows
    source venv/Scripts/activate
else
    # On macOS/Linux
    source venv/bin/activate
fi

# Install dependencies
pip install Flask Flask-SQLAlchemy requests fuzzywuzzy

# Run the application
python app.py

#~/Gaurav/venv/bin/python app.py
