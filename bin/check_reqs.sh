#!/bin/bash

. ./bin/env.sh

if "${VENV_HOME}/bin/python" -m pip install --dry-run -r requirements.txt > /dev/null 2>&1; then
    echo true
else
    echo false
fi

