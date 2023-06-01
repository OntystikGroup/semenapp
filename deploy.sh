#!/bin/bash

apt-get update && apt-get install ffmpeg libsm6 libxext6  -y

source venv/bin/activate
pip install -r requirements.txt
pip install python-multipart

mkdir api/input_photo
mkdir api/baw_images
mkdir api/output_photo

git fetch
expect ":"
send "$git_username\r"
expect ":"
send "$git_password\r"
git pull
expect "sername"
send "$git_username\r"
expect "assword"
send "$git_password\n"
git checkout new_original --force
expect "sername"
send "$git_username\r"
expect "assword"
send "$git_password\n"
uvicorn api.main:app --host 0.0.0.0 --port 8000
