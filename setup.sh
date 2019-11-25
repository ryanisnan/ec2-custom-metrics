#! /bin/bash

# Setup Virtualenv
pip install virtualenv
virtualenv venv
source venv/bin/activate

pip install -r requirements.txt