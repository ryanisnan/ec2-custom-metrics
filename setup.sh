#! /bin/bash

# Setup Virtualenv
pip3 install virtualenv
virtualenv venv -p python3
source venv/bin/activate

pip3 install -r requirements.txt