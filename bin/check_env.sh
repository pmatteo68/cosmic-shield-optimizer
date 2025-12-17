#!/bin/bash

. ./bin/env.sh

if [ -d "${VENV_HOME}" ] && \
   [ -f "${VENV_HOME}/pyvenv.cfg" ] && \
   [ -x "${VENV_HOME}/bin/python" ] && \
   "${VENV_HOME}/bin/python" -c 'import sys; exit(0 if sys.prefix != sys.base_prefix else 1)'; then
    echo true
else
    echo false
fi

