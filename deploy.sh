#!/bin/bash
sudo apt update
sudo apt install python3-pip python3-dev build-essential libssl-dev libffi-dev python3-setuptools

sudo apt install python3-virtualenv

virtualenv venv
source venv/bin/activate

pip install -r requirements.txt
sudo apt-get update && apt-get install ffmpeg libsm6 libxext6  -y

pip install gdown
cd model
gdown https://drive.google.com/uc?id=1EyY-aCaAt5xzwuCF98Zr-m_pu8fB3GvU

pip install python-multipart
sudo ufw allow 8001

sudo cp /root/projects/semenapp/semenapp.service /etc/systemd/system/

sudo systemctl start semenapp
sudo systemctl enable semenapp
sudo systemctl daemon-reload
sudo systemctl restart semenapp

sudo systemctl status semenapp
