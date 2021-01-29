#!/usr/bin/env bash

rm -fr  /home/arun/anaconda3/envs/arun/lib/python3.6/site-packages/alectiolite/
rm -rf ./build
rm -rf ./alectiolite.egg-info
rm -rf ./dist



python setup.py sdist bdist_wheel

pip install .
