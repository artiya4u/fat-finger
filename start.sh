#!/bin/bash

echo "killing uvicorn"
pkill -9 uvicorn

echo "starting uvicorn"
export PYTHONPATH=$PYTHONPATH:./app
nohup uvicorn api:app --host 0.0.0.0 --port 8008 &

echo "started"