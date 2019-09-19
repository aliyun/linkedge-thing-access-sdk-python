#!/bin/bash

PY3_VENV_PATH=/linkedge/gateway/build/bin/fc-runtime/linkedge/gateway/build/bin/py3_venv

TUNA_INDEX="https://pypi.tuna.tsinghua.edu.cn/simple"
TUNA_HOST="pypi.tuna.tsinghua.edu.cn"

ALIYUN_INDEX="https://mirrors.aliyun.com/pypi/simple/"
ALIYUN_HOST="mirrors.aliyun.com"

PIP3_INDEX_URL=$TUNA_INDEX
PIP3_TRUST_HOST=$TUNA_HOST

REQUIREMENTS=`readlink -f requirements.txt`
PACKAGES=`readlink -f packages`

PIP3="python3 -m pip --retries 0 --timeout 1 --disable-pip-version-check --trusted-host $PIP3_TRUST_HOST"
PIP3_INSTALL="$PIP3 install --index-url $PIP3_INDEX_URL -f $PACKAGES"

sudo mkdir -p $PY3_VENV_PATH
cd $PY3_VENV_PATH
sudo apt install python3-pip
sudo python3 -m pip install virtualenv
sudo python3 -m virtualenv .

sudo sh -c ". bin/activate; $PIP3_INSTALL -r $REQUIREMENTS"

